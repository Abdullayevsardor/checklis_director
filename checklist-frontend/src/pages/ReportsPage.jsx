import { useEffect, useState, useMemo } from "react";
import api from "../api/axios";
import { useNavigate } from "react-router-dom"; 


export default function ReportsPage() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    setLoading(true);
    api
      .get("/reports/shift-checks")
      .then((res) => setReports(res.data))
      .catch((err) => console.error("Ошибка загрузки отчетов:", err))
      .finally(() => setLoading(false));
  }, []);

  // 🕒 ISO vaqtni O'zbekiston vaqtiga o'girish
  const formatUzbDate = (isoString) => {
    if (!isoString) return "-";
    try {
      const date = new Date(isoString);
      return date.toLocaleString("uz-UZ", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Asia/Tashkent"
      });
    } catch (e) {
      return isoString;
    }
  };

  // 🏢 Backend ma'lumotidan filial nomini aniqlash logikasi
  const currentBranchName = useMemo(() => {
    if (reports.length === 0) return "Филиал";
    
    // Ro'yxatdagi birinchi elementning branch_id sini olamiz
    const firstItem = reports[0];
    const branchId = firstItem?.branch_id;

    if (branchId === 14) return "MW01 - UNIVERSAM";
    if (branchId === 26) return "MW02 - NEXT";
    if (branchId === 26) return "MW02 - NEXT";
    if (branchId === 26) return "MW02 - NEXT";
    if (branchId === 26) return "MW02 - NEXT";
    
    return firstItem?.branch?.name || firstItem?.branch_name || `Филиал (ID: ${branchId})`;
  }, [reports]);

  // Status bo'yicha filtrlash
  const filteredReports = useMemo(() => {
    return reports.filter((item) => statusFilter === "all" || item.status === statusFilter);
  }, [reports, statusFilter]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      
      {/* 📌 STICKY HEADER — Ekranda qotib turadigan yuqori qism */}
      <div className="sticky top-0 z-50 bg-white/95 backdrop-blur-md shadow-sm border-b border-gray-100 py-5 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Chap tomon: Orqaga tugmasi va Sarlavha */}
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => navigate(-1)} // 👈 MANA SHU FUNKSIYA ORQAGA QAYTARADI
              className="flex items-center justify-center w-10 h-10 rounded-xl border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:text-black active:scale-95 transition-all shadow-sm shrink-0 cursor-pointer"
              title="Назад"
            >
              {/* ⬅️ Strelka belgisi (SVG Ikonka) */}
              <svg xmlns="http://w3.org" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
            </button>

          </div>
        </div>
          
          <div>
            {/* 🏢 Taklifingiz bo'yicha: Filial nomi H1 hajmda yozildi */}
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-gray-950 flex items-center gap-2">
              <span>🏢</span> {currentBranchName}
            </h1>
            <p className="text-xs sm:text-sm text-gray-500 mt-1">
              Архив и мониторинг всех проверок смен по данному филиалу.
            </p>
          </div>
          
          {/* O'ng tomon: Status Filtr va jami soni */}
          <div className="flex items-center gap-3 self-end md:self-auto w-full md:w-auto justify-between md:justify-end">
            <div className="text-xs sm:text-sm font-semibold text-gray-600 bg-gray-100 px-3 py-2 rounded-xl">
              Всего: <span className="text-black font-bold">{filteredReports.length}</span>
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-xs sm:text-sm outline-none focus:ring-2 focus:ring-black focus:bg-white transition-all font-medium cursor-pointer"
            >
              <option value="all">Все статусы</option>
              <option value="submitted">✓ Отправлено</option>
              <option value="draft">⏳ Черновик</option>
            </select>
          </div>
        </div>
      
    

      {/* 🏢 JADVAL MA'LUMOTLARI */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {loading ? (
          <div className="text-center py-20 space-y-3">
            <div className="w-8 h-8 border-2 border-black border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-gray-500 font-medium">Загрузка отчетов...</p>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="text-center py-20 text-gray-500 bg-white rounded-2xl border border-gray-100 shadow-sm">
            <span className="text-3xl">📭</span>
            <p className="mt-2 font-medium text-sm">В этом статусе записей не найдено.</p>
          </div>
        ) : (
          <>
            {/* 1️⃣ DESKTOP TABLE VIEW — Kompyuter uchun (Filial qatori olib tashlandi) */}
            <div className="hidden md:block bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <table className="w-full border-collapse text-left">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider w-10">ID</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-center w-80  ">Статус</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider w-50">Начато </th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider w-50">Отправлено </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-sm">
                  {filteredReports.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-6 py-4 font-mono font-bold text-gray-400">  {item.id}</td>
                      <td className="px-6 py-4 text-center">
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold ${
                          item.status === "submitted"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                            : "bg-amber-50 text-amber-700 border border-amber-100"
                        }`}>
                          {item.status === "submitted" ? "✓ Отправлено" : "⏳ Черновик"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-500 font-medium">{formatUzbDate(item.started_at)}</td>
                      <td className="px-6 py-4 text-gray-500 font-medium">{formatUzbDate(item.submitted_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* 2️⃣ MOBILE CARD VIEW — Telefonlar uchun (Filial qatori olib tashlandi) */}
            <div className="block md:hidden space-y-4">
              {filteredReports.map((item) => (
                <div 
                  key={item.id} 
                  className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 space-y-3"
                >
                  <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                    <span className="font-mono font-bold text-gray-400">#{item.id}</span>
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                      item.status === "submitted"
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                        : "bg-amber-50 text-amber-700 border border-amber-100"
                    }`}>
                      {item.status === "submitted" ? "✓ Отправлено" : "⏳ Черновик"}
                    </span>
                  </div>

                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-400">📅 Начато:</span>
                      <span className="text-gray-700 font-medium">{formatUzbDate(item.started_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">📤 Отправлено:</span>
                      <span className="text-gray-700 font-medium">{formatUzbDate(item.submitted_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

      </div>
    </div>
  );
}
