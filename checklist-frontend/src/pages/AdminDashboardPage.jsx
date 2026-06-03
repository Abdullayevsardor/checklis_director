import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import BranchDetailsModal from "./BranchDetailsModal"; // 1-QADAM: To'g'ri import qilindi

export default function AdminDashboardPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("branches"); // Filiallar bo'limi standart ochiladi
  const [stats, setStats] = useState({
    totalShiftChecks: 0,
    submittedChecks: 0,
    draftChecks: 0,
    branches: [],
  });
  const [loading, setLoading] = useState(true);
  
  // 2-QADAM: Tanlangan filial davlati
  const [selectedBranch, setSelectedBranch] = useState(null);

  const [faceIdLoading, setFaceIdLoading] = useState(false);
  const [faceIdMessage, setFaceIdMessage] = useState({ type: "", text: "" });

  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    loadAdminData();
  }, []);

async function loadAdminData() {
  setLoading(true);
  try {
    // ⚠️ MANZILNI MANA SHUNDAY TO'LIQ YOZING (boshida /shift-checks bo'lishi shart):
    const res = await api.get("/shift-checks/dashboard-stats");
    
    const branchStats = res.data || [];

    const totalChecks = branchStats.reduce((sum, b) => sum + (Number(b.total) || 0), 0);
    const totalSubmitted = branchStats.reduce((sum, b) => sum + (Number(b.submitted) || 0), 0);
    const totalDraft = branchStats.reduce((sum, b) => sum + (Number(b.draft) || 0), 0);

    setStats({
      totalShiftChecks: totalChecks,
      submittedChecks: totalSubmitted,
      draftChecks: totalDraft,
      branches: branchStats,
    });
  } catch (err) {
    console.error("Dashboard ma'lumotlarini yuklashda xatolik:", err);
  } finally {
    setLoading(false);
  }
}


function bufferToBase64Url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
  }

  async function handleRegisterFaceID() {
    setFaceIdLoading(true);
    setFaceIdMessage({ type: "", text: "" });
    try {
      const challengeRes = await api.post("/auth/face-id/register/challenge");
      const backendData = challengeRes.data;
      const rawChallenge = Uint8Array.from(atob(backendData.challenge.replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0)).buffer;
      const rawUserId = new TextEncoder().encode(backendData.user_id);

      const webAuthnOptions = {
        challenge: rawChallenge,
        rp: { name: "Shift Checklist System", id: window.location.hostname },
        user: { id: rawUserId, name: backendData.user_name, displayName: backendData.user_display_name },
        pubKeyCredParams: [{ type: "public-key", alg: -7 }, { type: "public-key", alg: -257 }]
      };

      const credential = await navigator.credentials.create({ publicKey: webAuthnOptions });
      const registerPayload = {
        credential_id: credential.id,
        attestation_object: bufferToBase64Url(credential.response.attestationObject),
        client_data_json: bufferToBase64Url(credential.response.clientDataJSON),
        device_name: navigator.userAgent.slice(0, 30)
      };

      const verifyRes = await api.post("/auth/face-id/register/verify", registerPayload);
      setFaceIdMessage({ type: "success", text: verifyRes.data.message || "Face ID успешно подключен!" });
    } catch (err) {
      console.error(err);
      setFaceIdMessage({ type: "error", text: "Ошибка при подключении Face ID" });
    } finally {
      setFaceIdLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/");
  }

  const branchChartData = [...stats.branches].sort((a, b) => b.completion - a.completion);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Админ Панель</h1>
            <p className="text-gray-500 text-sm">Пользователь: {user.full_name} ({user.role})</p>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={loadAdminData} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
              🔄 Обновить
            </button>
            <button onClick={handleLogout} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium">
              🚪 Выход
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 flex gap-8">
          {[
            { id: "overview", name: "📊 Общий обзор" },
            { id: "branches", name: "🏢 Филиалы" },
            { id: "charts", name: "📈 Графика" },
            { id: "faceid", name: "🔒 Подключить Face ID" }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-4 font-medium border-b-2 transition-colors ${
                activeTab === tab.id ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-800"
              }`}
            >
              {tab.name}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12"><p className="text-gray-500">Загрузка...</p></div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === "overview" && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-600">
                  <p className="text-gray-500 text-sm font-medium">Всего Чеклистов</p>
                  <p className="text-3xl font-bold mt-2">{stats.totalShiftChecks}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow border-l-4 border-emerald-500">
                  <p className="text-gray-500 text-sm font-medium">Завершено</p>
                  <p className="text-3xl font-bold mt-2 text-emerald-600">{stats.submittedChecks}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow border-l-4 border-amber-500">
                  <p className="text-gray-500 text-sm font-medium">Черновики</p>
                  <p className="text-3xl font-bold mt-2 text-amber-500">{stats.draftChecks}</p>
                </div>
              </div>
            )}

            {/* Branches Tab */}
            {activeTab === "branches" && (
              <div className="bg-white rounded-xl shadow overflow-hidden border border-gray-100">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Название филиала</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Всего</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Завершено</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Черновики</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Выполнение %</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {stats.branches.map((branch) => (
                      <tr key={branch.id} className="hover:bg-gray-50 transition">
                        {/* Filial nomi bosilganda modal ochiladi */}
                        <td 
                          className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600 hover:text-blue-800 cursor-pointer underline decoration-dotted" 
                          onClick={() => setSelectedBranch(branch)}
                        >
                          {branch.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{branch.total}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600">{branch.submitted}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-amber-500">{branch.draft}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <div className="w-24 bg-gray-200 rounded-full h-2">
                              <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${branch.completion}%` }}></div>
                            </div>
                            <span className="text-sm font-semibold text-gray-700">{branch.completion}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Charts Tab */}
            {activeTab === "charts" && (
              <div className="w-full bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="h-[500px] md:h-96 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={branchChartData} layout={window.innerWidth < 768 ? "vertical" : "horizontal"} margin={window.innerWidth < 768 ? { top: 10, right: 20, left: 20, bottom: 10 } : { top: 10, right: 10, left: -20, bottom: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={window.innerWidth < 768} horizontal={window.innerWidth >= 768} />
                      <XAxis type={window.innerWidth < 768 ? "number" : "category"} dataKey={window.innerWidth < 768 ? undefined : "name"} tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} interval={0} angle={window.innerWidth < 768 ? 0 : -45} textAnchor={window.innerWidth < 768 ? "middle" : "end"} />
                      <YAxis type={window.innerWidth < 768 ? "category" : "number"} dataKey={window.innerWidth < 768 ? "name" : undefined} tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} width={window.innerWidth < 768 ? 90 : 40} />
                      <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #f0f0f0' }} />
                      <Legend verticalAlign="top" height={40} iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '12px' }} />
                      <Bar dataKey="submitted" name="Завершено" fill="#10b981" stackId="a" />
                      <Bar dataKey="draft" name="Черновики" fill="#f59e0b" stackId="a" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Face ID Tab */}
            {activeTab === "faceid" && (
              <div className="max-w-md mx-auto bg-white p-8 rounded-xl shadow text-center border">
                <h3 className="text-xl font-bold mb-2">Биометрическая привязка Face ID</h3>
                <p className="text-gray-500 text-sm mb-6">Зарегистрируйте устройство для быстрого входа без пароля.</p>
                <button onClick={handleRegisterFaceID} disabled={faceIdLoading} className="w-full py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50">
                  {faceIdLoading ? "Ожидание сканера..." : "🔒 Подключить устройство"}
                </button>
                {faceIdMessage.text && <div className="mt-4 p-3 rounded-lg text-sm bg-gray-50">{faceIdMessage.text}</div>}
              </div>
            )}
          </>
        )}
      </div>

      {/* 3-QADAM: Alohida fayldan kelgan modal oyna yuklandi */}
      <BranchDetailsModal 
        branch={selectedBranch} 
        onClose={() => setSelectedBranch(null)} 
      />
    </div>
  );
}
