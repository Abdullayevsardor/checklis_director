import { useState, useEffect } from "react";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";
import FaceRecognition from "../components/FaceRecognition";

export default function LoginPage() {
  const navigate = useNavigate();

  const [branches, setBranches] = useState([]);
  const [branchId, setBranchId] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false); // 👈 Yangi: Parolni ko'rsatish/yashirish holati
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loginMode, setLoginMode] = useState("director"); // 'director', 'admin-password', 'admin-face'

  useEffect(() => {
    if (loginMode === "director") {
      loadBranches();
    }
    // Har safar rejim o'zgarganda parolni yashirib qo'yamiz va tozalaymiz
    setPassword("");
    setShowPassword(false);
  }, [loginMode]);

  async function loadBranches() {
    try {
      const res = await api.get("/branches");
      setBranches(res.data);
      if (res.data.length > 0) {
        setBranchId(res.data[0].id);
      }
    } catch (err) {
      console.log("Не удалось загрузить филиалы", err);
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.post("/auth/login", {
        password: password,
        branch_id: loginMode === "director" ? parseInt(branchId) : 0,
      });

      localStorage.setItem("access_token", res.data.access_token);
      const userData = res.data.user;
      localStorage.setItem("user", JSON.stringify(userData));

      if (userData.role === "admin") {
        navigate("/admin-dashboard");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка входа");
      console.log(err);
    } finally {
      setLoading(false);
    }
  }

  function handleFaceLoginSuccess(user) {
    if (user.role === "admin") {
      navigate("/admin-dashboard");
    } else {
      navigate("/dashboard");
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-lg p-6">
        <h1 className="text-2xl font-bold text-center mb-2">
          Система чек-листов
        </h1>

        {/* Login Mode Tabs */}
        <div style={{ display: "flex", gap: 6, marginBottom: 20, flexWrap: "wrap" }}>
          <button
            type="button"
            onClick={() => setLoginMode("director")}
            style={{
              flex: 1,
              minWidth: "100px",
              padding: "8px 10px",
              border: "none",
              borderRadius: 6,
              background: loginMode === "director" ? "#111" : "#eee",
              color: loginMode === "director" ? "#fff" : "#111",
              cursor: "pointer",
              fontWeight: 500,
              fontSize: 13,
            }}
          >
            Директор
          </button>
          <button
            type="button"
            onClick={() => setLoginMode("admin-password")}
            style={{
              flex: 1,
              minWidth: "100px",
              padding: "8px 10px",
              border: "none",
              borderRadius: 6,
              background: loginMode === "admin-password" ? "#111" : "#eee",
              color: loginMode === "admin-password" ? "#fff" : "#111",
              cursor: "pointer",
              fontWeight: 500,
              fontSize: 13,
            }}
          >
            Admin
          </button>
          <button
            type="button"
            onClick={() => setLoginMode("admin-face")}
            style={{
              flex: 1,
              minWidth: "100px",
              padding: "8px 10px",
              border: "none",
              borderRadius: 6,
              background: loginMode === "admin-face" ? "#111" : "#eee",
              color: loginMode === "admin-face" ? "#fff" : "#111",
              cursor: "pointer",
              fontWeight: 500,
              fontSize: 13,
            }}
          >
            Face ID
          </button>
        </div>

        <p className="text-center text-gray-500 mb-6 text-sm">
          {loginMode === "director"
            ? "Filial uchun parol bilan kirish."
            : loginMode === "admin-password"
            ? "Admin uchun parol bilan kirish."
            : "Admin Face ID bilan kirish. Kamera ochiladi va yuz tanlanadi."}
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Director Password Login */}
        {loginMode === "director" && (
          <form onSubmit={handleLogin} className="space-y-4">
            {/* console.log("Response:", res.data);
            console.log("Token:", res.data.access_token);  */}

            <select
              className="w-full border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-black"
              value={branchId}
              onChange={(e) => setBranchId(e.target.value)}
            >
              <option value="">Выберите филиал</option>
              {branches.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>

            {/* 🔒 Ko'zcha tugmali parol bloki */}
            <div className="relative">
              <input
                className="w-full border rounded-xl pl-4 pr-12 py-3 outline-none focus:ring-2 focus:ring-black"
                type={showPassword ? "text" : "password"} // 👈 Dinamik tur
                placeholder="Пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black cursor-pointer text-lg select-none"
              >
                {showPassword ? "👁️" : "🙈"}
              </button>
            </div>

            <button
              type="submit"
              disabled={loading || !branchId || !password}
              className="w-full bg-black text-white rounded-xl py-3 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Вход..." : "Войти"}
            </button>
          </form>
        )}

        {/* Admin Password Login */}
        {loginMode === "admin-password" && (
          <form onSubmit={handleLogin} className="space-y-4">
            {/* 🔒 Ko'zcha tugmali parol bloki */}
            <div className="relative">
              <input
                className="w-full border rounded-xl pl-4 pr-12 py-3 outline-none focus:ring-2 focus:ring-black"
                type={showPassword ? "text" : "password"} // 👈 Dinamik tur
                placeholder="Пароль администратора"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black cursor-pointer text-lg select-none"
              >
                {showPassword ? "🙈" : "👁️"}
              </button>
            </div>

            <button
              type="submit"
              disabled={loading || !password}
              className="w-full bg-black text-white rounded-xl py-3 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Вход..." : "Войти"}
            </button>
          </form>
        )}

        {/* Admin Face ID Login */}
        {loginMode === "admin-face" && (
          <FaceRecognition onLoginSuccess={handleFaceLoginSuccess} />
        )}
      </div>
    </div>
  );
}
