import { useEffect, useRef, useState } from "react";
import api from "../api/axios";

function bufferToBase64Url(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function base64UrlToBuffer(base64Url) {
  const padding = "=".repeat((4 - (base64Url.length % 4)) % 4);
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/") + padding;
  const binary = window.atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

export default function FaceRecognition({ onLoginSuccess }) {
  const videoRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Kamera sinovga tayyorlanmoqda...");
  const [cameraActive, setCameraActive] = useState(false);
  const [challengeData, setChallengeData] = useState(null);
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    if (!window.PublicKeyCredential || !navigator.credentials) {
      setSupported(false);
      setStatus("Brauzeringiz WebAuthn yoki Face ID'ni qo'llab-quvvatlamaydi.");
      return;
    }

    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraActive(true);
      setStatus("Kameradan foydalanish ruxsat etildi. Face ID ni boshlash uchun pastdagi tugmani bosing.");
      setError("");
    } catch (err) {
      setCameraActive(false);
      setSupported(false);
      setStatus("Kamera ochilmadi. Iltimos, brauzeringizda kamera ruxsatini tekshiring.");
      console.error(err);
    }
  }

  function stopCamera() {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  }

  async function loadChallenge() {
    try {
      const res = await api.post("/auth/face-id/challenge");
      setChallengeData(res.data);
      return res.data;
    } catch (err) {
      console.error(err);
      setError("Face ID chaqiruvini olishda xatolik yuz berdi.");
      throw err;
    }
  }

  async function startFaceId() {
    if (!supported) return;
    setLoading(true);
    setError("");
    setStatus("Face ID uchun autentifikatsiya boshlanmoqda...");

    try {
      const challenge = challengeData || (await loadChallenge());
      
      // WebAuthn configuration - rpId must match backend RP_ID exactly
      const rpId = window.location.hostname; // 'localhost', '127.0.0.1', or your domain
      const origin = window.location.origin; // 'http://localhost:5173', etc.
      
      console.log("[WebAuthn Debug] RP_ID:", rpId);
      console.log("[WebAuthn Debug] Origin:", origin);
      console.log("[WebAuthn Debug] Hostname:", window.location.hostname);
      console.log("[WebAuthn Debug] Challenge:", challenge.challenge);
      
      const assertion = await navigator.credentials.get({
        publicKey: {
          challenge: base64UrlToBuffer(challenge.challenge),
          allowCredentials: challenge.allowed_credentials.map((cred) => ({
            id: base64UrlToBuffer(cred.id),
            type: cred.type,
          })),
          timeout: 60000,
          userVerification: "required",
          rpId: rpId,
        },
      });

      if (!assertion) {
        throw new Error("Face ID dan javob olinmadi");
      }

      const response = assertion.response;
      const payload = {
        credential_id: assertion.id,
        challenge: challenge.challenge,
        client_data_json: bufferToBase64Url(response.clientDataJSON),
        authenticator_data: bufferToBase64Url(response.authenticatorData),
        signature: bufferToBase64Url(response.signature),
      };

      const verifyRes = await api.post("/auth/face-id/verify", payload);
      localStorage.setItem("access_token", verifyRes.data.access_token);
      localStorage.setItem("user", JSON.stringify(verifyRes.data.user));
      stopCamera();
      onLoginSuccess(verifyRes.data.user);
    } catch (err) {
      console.error("[FaceRecognition Error]", err);
      
      // Detailed error handling for WebAuthn-specific errors
      let errorMessage = err.message || "Face ID autentifikatsiyasida xatolik";
      
      if (err.name === "NotAllowedError") {
        errorMessage = "Operatsiya rad etildi. Brauzer ruxsatini tekshiring yoki boshqa usulni tanlang.";
      } else if (err.name === "InvalidStateError") {
        errorMessage = "Bu qurilma allaqachon registersiya qilingan. Boshqa qurilmadan urinib ko'ring.";
      } else if (err.name === "NotSupportedError") {
        errorMessage = "Bu brauzer WebAuthn/Face ID'ni qo'llab-quvvatlamaydi.";
      } else if (err.name === "TimeoutError") {
        errorMessage = "Vaqt tugadi. Qayta urinib ko'ring.";
      } else if (err.message?.includes("rpId")) {
        errorMessage = "Domenil mismatch. localhost va 127.0.0.1 farqli bo'lishi mumkin.";
      }
      
      setError(errorMessage);
      setStatus("Face ID sinovini qayta boshlang yoki boshqa usulni tanlang.");
      console.error("[Full Error Object]", {
        name: err.name,
        message: err.message,
        code: err.code,
        stack: err.stack
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full space-y-4">
      <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 shadow-sm">
        <div className="flex items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-lg font-semibold">Face ID orqali kirish</h2>
            <p className="text-sm text-slate-600">Kamera ochiladi va admin yuzini tekshirishga harakat qilinadi.</p>
          </div>
          <div className="inline-flex items-center justify-center rounded-2xl bg-blue-600 p-3 text-white">
            <span className="text-xl">🪪</span>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-black/5">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="h-72 w-full object-cover"
          />
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent" />
          <div className="pointer-events-none absolute inset-x-0 bottom-0 p-4 text-white">
            <p className="text-sm font-semibold">Kameradan yuz tanish</p>
            <p className="text-xs text-slate-200">Agar kamera ishlamasa, brauzer ruxsatini tekshiring.</p>
          </div>
        </div>

        <div className="mt-4 rounded-3xl bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-700">{status}</p>
          {error && (
            <div className="mt-3 rounded-2xl bg-red-50 p-3 text-sm text-red-700 border border-red-100">
              {error}
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={startFaceId}
          disabled={loading || !supported}
          className="mt-4 w-full rounded-3xl bg-gradient-to-r from-blue-600 to-cyan-500 px-5 py-3 text-sm font-semibold text-white shadow-lg transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Face ID tekshirilmoqda..." : "Face IDni boshlash"}
        </button>
      </div>
    </div>
  );
}
