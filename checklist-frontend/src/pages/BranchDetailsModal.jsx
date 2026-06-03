import { useEffect, useState } from "react";
import api from "../api/axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function buildPhotoUrl(url) {
  if (!url) return null;
  if (url.startsWith("http") || url.startsWith("blob:") || url.startsWith("data:")) return url;
  return `${API_BASE_URL}${url}`;
}

function formatDate(isoString) {
  if (!isoString) return "—";
  try {
    return new Date(isoString).toLocaleString("ru-RU", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Asia/Tashkent",
    });
  } catch {
    return isoString;
  }
}

function StatusBadge({ status }) {
  const s = String(status || "").toLowerCase();
  const isYes = s === "yes" || s === "да";
  const isNo = s === "no" || s === "нет";
  const isSubmitted = s === "submitted" || s === "completed" || s === "finished";

  const baseStyles = "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium backdrop-blur-md";

  if (isSubmitted || isYes) {
    return (
      <span className={`${baseStyles} bg-emerald-500/10 text-emerald-600 dark:text-emerald-400`}>
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        {isSubmitted ? "Отправлен" : "Да"}
      </span>
    );
  }
  if (isNo) {
    return (
      <span className={`${baseStyles} bg-rose-500/10 text-rose-600 dark:text-rose-400`}>
        <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
        Нет
      </span>
    );
  }
  return (
    <span className={`${baseStyles} bg-amber-500/10 text-amber-600 dark:text-amber-400`}>
      <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
      {status || "В процессе"}
    </span>
  );
}

function AnswerRow({ answer }) {
  const [imgOpen, setImgOpen] = useState(false);

  const photos = answer.photos?.length
    ? answer.photos
    : answer.photo_url
    ? [{ file_url: answer.photo_url }]
    : [];

  const firstPhoto = buildPhotoUrl(photos[0]?.file_url);
  const isYes = ["yes", "да"].includes(String(answer.status || "").toLowerCase());
  const isNo = ["no", "нет"].includes(String(answer.status || "").toLowerCase());

  return (
    <div className="flex gap-4 py-3.5 first:pt-1 last:pb-1 group">
      <div className="flex flex-col items-center pt-1.5">
        <div className={`w-2 h-2 rounded-full transition-all duration-300 ${
          isYes ? "bg-emerald-500 ring-4 ring-emerald-500/10" : 
          isNo ? "bg-rose-500 ring-4 ring-rose-500/10" : "bg-gray-300"
        }`} />
        <div className="w-[1px] flex-1 bg-gray-100 mt-2 group-last:hidden" />
      </div>

      <div className="flex-1 space-y-2">
        <p className="text-[14px] font-medium text-gray-900 leading-normal">
          {answer.item_title_ru || answer.item_title || `Пункт #${answer.item_id}`}
        </p>

        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={answer.status} />
          {answer.comment && (
            <span className="text-[12px] text-gray-500 bg-gray-50 px-2.5 py-0.5 rounded-md max-w-xs truncate">
              {answer.comment}
            </span>
          )}
        </div>

        {firstPhoto && (
          <div className="pt-1">
            <button
              type="button"
              onClick={() => setImgOpen(true)}
              className="relative w-24 h-24 rounded-xl overflow-hidden border border-gray-100/50 bg-gray-50 block hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
            >
              <img
                src={firstPhoto}
                alt="Photo"
                className="w-full h-full object-cover"
                onError={(e) => (e.target.parentElement.style.display = "none")}
              />
            </button>

            {imgOpen && (
              <div
                className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-md p-4 transition-opacity duration-300"
                onClick={() => setImgOpen(false)}
              >
                <div className="relative max-w-3xl w-full" onClick={(e) => e.stopPropagation()}>
                  <img src={firstPhoto} alt="Zoomed" className="w-full rounded-2xl max-h-[85vh] object-contain mx-auto" />
                  <button
                    onClick={() => setImgOpen(false)}
                    className="absolute -top-12 right-0 w-10 h-10 rounded-full bg-white/10 text-white flex items-center justify-center hover:bg-white/20 transition-all text-xl"
                  >
                    ×
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function CheckCard({ check }) {
  const [expanded, setExpanded] = useState(false);

  const isFinished = ["submitted", "completed", "finished"].includes(check.status);
  const answers = check.answers || [];
  const yesCount = answers.filter(a => ["yes", "да"].includes(String(a.status).toLowerCase())).length;
  const noCount = answers.filter(a => ["no", "нет"].includes(String(a.status).toLowerCase())).length;
  const total = answers.length;

  return (
    <div className="bg-white rounded-2xl border border-gray-100/80 overflow-hidden transition-all duration-300 hover:border-gray-200">
      <div
        className="flex items-center justify-between p-4 cursor-pointer select-none active:bg-gray-50/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3.5 min-w-0">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-sm font-semibold ${
            isFinished ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"
          }`}>
            {isFinished ? "✓" : "···"}
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-900">Чек-лист #{check.id}</span>
              <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                isFinished ? "bg-gray-900 text-white" : "bg-amber-500/10 text-amber-700"
              }`}>
                {isFinished ? "Отправлен" : "Черновик"}
              </span>
            </div>
            <p className="text-[11px] text-gray-400 mt-0.5 font-medium">
              {formatDate(check.submitted_at || check.started_at)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          {total > 0 && (
            <div className="hidden sm:flex items-center gap-2 text-[11px] font-medium text-gray-400">
              <span className="text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded">{yesCount} ✓</span>
              <span className="text-rose-600 font-semibold bg-rose-50 px-2 py-0.5 rounded">{noCount} ✗</span>
              <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{total} всего</span>
            </div>
          )}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`w-4 h-4 text-gray-400 transition-transform duration-300 ${expanded ? "rotate-180" : ""}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {total > 0 && (
        <div className="px-4 pb-3">
          <div className="w-full h-[3px] bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-500"
              style={{ width: `${(yesCount / total) * 100}%` }}
            />
          </div>
        </div>
      )}

      <div className={`grid transition-all duration-300 ease-in-out ${expanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}>
        <div className="overflow-hidden bg-gray-50/40 px-4">
          <div className="py-2 divide-y divide-gray-100/60">
            {answers.length === 0 ? (
              <p className="text-xs text-gray-400 italic text-center py-6">Ответы не найдены</p>
            ) : (
              answers.map((answer, i) => <AnswerRow key={answer.id ?? i} answer={answer} />)
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function BranchDetailsModal({ branch, onClose }) {
  const [branchDetails, setBranchDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, submitted: 0, draft: 0 });

  useEffect(() => {
    if (branch) loadBranchDetails();
  }, [branch]);

  async function loadBranchDetails() {
    setLoading(true);
    try {
      const res = await api.get(`/branches/${branch.id}/shift-checks`);
      const data = res.data;
      setBranchDetails(data);

      const submitted = data.filter(c => ["submitted", "completed", "finished"].includes(c.status)).length;
      setStats({ total: data.length, submitted, draft: data.length - submitted });
    } catch (err) {
      console.error("Xatolik:", err);
    } finally {
      setLoading(false);
    }
  }

  if (!branch) return null;

  const initials = branch.name?.split(" ").slice(0, 2).map(w => w[0]).join("").toUpperCase() || "?";

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-6">
      {/* Backdrop shadow */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300" onClick={onClose} />

      {/* MODAL CONTAINER: Katta ekranlarda (sm:) max-w-3xl qildik (Kengaydi) */}
      <div className="relative bg-white w-full sm:max-w-3xl h-[92vh] sm:h-auto max-h-[92vh] sm:max-h-[85vh] rounded-t-[24px] sm:rounded-[24px] shadow-2xl flex flex-col overflow-hidden border border-gray-100 transition-transform duration-300 transform translate-y-0">
        <div className="w-12 h-1 bg-gray-200 rounded-full mx-auto my-2.5 sm:hidden flex-shrink-0" />

        {/* Header */}
        <div className="px-6 pb-4 pt-2 sm:pt-5 border-b border-gray-100 flex-shrink-0">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3.5 min-w-0">
              <div className="w-11 h-11 rounded-xl bg-gray-950 text-white flex items-center justify-center text-sm font-bold tracking-wider">
                {initials}
              </div>
              <div className="min-w-0">
                <h3 className="text-lg font-bold text-gray-950 truncate">{branch.name}</h3>
                <p className="text-xs text-gray-400 font-medium">История проверок смен</p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full hidden sm:flex items-center justify-center bg-gray-50 text-gray-400 hover:bg-gray-100 transition-all text-xl"
            >
              ×
            </button>
          </div>

          {/* Statistika qismini ham chiroyli katakchalarga joyladik */}
          {!loading && stats.total > 0 && (
            <div className="mt-4 flex gap-6 border-t border-gray-100 pt-3">
              {[
                { label: "Всего проверок", value: stats.total, color: "text-gray-950" },
                { label: "Отправлено", value: stats.submitted, color: "text-emerald-600" },
                { label: "Черновики", value: stats.draft, color: "text-amber-600" },
              ].map((s) => (
                <div key={s.label} className="text-left">
                  <p className={`text-lg font-extrabold leading-none ${s.color}`}>{s.value}</p>
                  <p className="text-[11px] font-semibold text-gray-400 mt-1 uppercase tracking-wider">{s.label}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50/50">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <div className="w-6 h-6 border-2 border-gray-900 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-gray-400 font-medium">Загрузка данных...</p>
            </div>
          ) : branchDetails.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-2 text-center">
              <span className="text-3xl">📭</span>
              <p className="font-semibold text-gray-800 text-sm mt-2">Нет данных</p>
              <p className="text-xs text-gray-400">Ни одной проверки не найдено</p>
            </div>
          ) : (
            branchDetails.map((check) => <CheckCard key={check.id} check={check} />)
          )}
        </div>

        {/* Footer */}
        <div className="p-6 bg-white border-t border-gray-100 flex-shrink-0">
          <button
            onClick={onClose}
            className="w-full py-3.5 bg-gray-900 hover:bg-black text-white text-sm font-semibold rounded-xl active:scale-[0.98] transition-all duration-150 shadow-md shadow-gray-950/10"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
}