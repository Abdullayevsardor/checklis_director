import axios from "../api/axios";

export async function testFaceIdSetup() {
  console.log("\n🔍 === Face ID Setup Test ===\n");
  
  // 1. Check frontend environment
  console.log("📱 FRONTEND ENVIRONMENT:");
  console.log("  • Hostname:", window.location.hostname);
  console.log("  • Origin:", window.location.origin);
  console.log("  • Protocol:", window.location.protocol);
  console.log("  • Port:", window.location.port || "default");
  
  // 2. Check WebAuthn support
  console.log("\n🔐 WEBAUTHN SUPPORT:");
  console.log("  • PublicKeyCredential:", !!window.PublicKeyCredential);
  console.log("  • navigator.credentials:", !!navigator.credentials);
  
  if (!window.PublicKeyCredential) {
    console.error("  ❌ WebAuthn NOT supported!");
    return;
  }
  
  // 3. Try to get challenge
  console.log("\n📡 CHALLENGE REQUEST:");
  try {
    const res = await axios.post("/auth/face-id/challenge");
    console.log("  ✅ Challenge received:");
    console.log("  • Challenge length:", res.data.challenge.length);
    console.log("  • Allowed credentials:", res.data.allowed_credentials.length);
    
    // 4. Decode and check challenge
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
    
    const challengeBuffer = base64UrlToBuffer(res.data.challenge);
    console.log("  • Challenge buffer length:", challengeBuffer.byteLength);
    
    // 5. Try isUserVerifyingPlatformAuthenticatorAvailable
    console.log("\n🔒 PLATFORM AUTHENTICATOR CHECK:");
    const isAvailable = await window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    console.log("  • Platform authenticator available:", isAvailable);
    
    if (!isAvailable) {
      console.warn("  ⚠️  Platform authenticator (Face ID / fingerprint) not available on this device");
    }
    
    // 6. Check if we can list credentials (if supported)
    console.log("\n💾 CREDENTIALS CHECK:");
    if (navigator.credentials.get) {
      console.log("  ✅ navigator.credentials.get is available");
    }
    
  } catch (err) {
    console.error("  ❌ Challenge request failed:", err.message);
    console.error("  Full error:", err);
  }
}

// Run test when imported
if (typeof window !== 'undefined') {
  // Wait a bit for React to initialize
  setTimeout(() => {
    window.testFaceIdSetup = testFaceIdSetup;
    console.log("💡 Run window.testFaceIdSetup() in console to test Face ID");
  }, 1000);
}
