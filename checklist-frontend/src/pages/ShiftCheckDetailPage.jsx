import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { uploadPhotoFile } from "../services/uploadService";
import toast from "react-hot-toast";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function buildPhotoUrl(url) {
  if (!url) return null;
  if (
    url.startsWith("http") ||
    url.startsWith("blob:") ||
    url.startsWith("data:")
  ) {
    return url;
  }
  return `${API_BASE_URL}${url}`;
}

export default function ShiftCheckDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [shift, setShift] = useState(null);
  const [checklist, setChecklist] = useState([]);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [confirmOpen, setConfirmOpen] = useState(false);

  // answers ni ref da ham saqlaymiz — stale closure muammosi uchun
  const answersRef = useRef({});
  useEffect(() => {
    answersRef.current = answers;
  }, [answers]);

  // loadData — faqat ilk yuklashda va xato retry da ishlatiladi
  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [shiftRes, checklistRes] = await Promise.all([
        api.get(`/shift-checks/${id}`),
        api.get("/checklist"),
      ]);

      const saved = {};
      shiftRes.data.answers?.forEach((answer) => {
        const photos =
          answer.photos?.map((photo) => ({
            file_url: photo.file_url,
            thumbnail_url: photo.thumbnail_url,
            file_size: photo.file_size,
            mime_type: photo.mime_type,
          })) ?? [];

        if (
          answer.photo_url &&
          !photos.some((photo) => photo.file_url === answer.photo_url)
        ) {
          photos.unshift({ file_url: answer.photo_url });
        }

        saved[answer.item_id] = {
          status: answer.status || "",
          comment: answer.comment || "",
          photos,
        };
      });

      setShift(shiftRes.data);
      setAnswers(saved);
      answersRef.current = saved;
      setChecklist(checklistRes.data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || err.message || "Ошибка загрузки данных"
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  function handleAnswerChange(itemId, field, value) {
    setAnswers((prev) => {
      const updated = {
        ...prev,
        [itemId]: {
          ...prev[itemId],
          [field]: value,
        },
      };
      answersRef.current = updated;
      return updated;
    });
  }

async function uploadPhoto(itemId, file) {
  if (!file) return;

  const existingPhotos = answersRef.current[itemId]?.photos ?? [];
  const localUrl = URL.createObjectURL(file);
  
  // Faqat ekranda preview ko'rsatish uchun stateni yangilaymiz (Lekin bazaga SAQLAMAYMIZ)
  setAnswers((prev) => ({
    ...prev,
    [itemId]: { ...prev[itemId], photos: [{ file_url: localUrl }] }
  }));

  try {
    // 1. Rasmni haqiqiy serverga yuklaymiz
    const uploadedPhoto = await uploadPhotoFile(file); 

    // 2. State va Ref-ni serverdan kelgan to'g'ri URL bilan yangilaymiz
    const updatedAnswers = {
      ...answersRef.current,
      [itemId]: {
        ...answersRef.current[itemId],
        photos: [uploadedPhoto] // Yangi rasm obyekti
      }
    };
    
    setAnswers(updatedAnswers);
    answersRef.current = updatedAnswers;

    toast.success("Фото успешно загружено на сервер");

    // 3. Endi xavfsiz ravishda bazaga yozsak bo'ladi, chunki ref ichida haqiqiy URL turibdi
    await saveItemAnswer(itemId); 
  } catch (err) {
    console.error(err);
    handleAnswerChange(itemId, "photos", existingPhotos);
    toast.error("Ошибка при загрузке фото");
  } finally {
    URL.revokeObjectURL(localUrl);
  }
}


const saveItemAnswer = useCallback(
  async (itemId, forcedStatus = null) => {
    const currentAnswers = answersRef.current;
    const currentStatus = forcedStatus ?? currentAnswers[itemId]?.status ?? "";
    const currentComment = currentAnswers[itemId]?.comment ?? "";
    const currentPhotos = currentAnswers[itemId]?.photos ?? [];

    if (!currentStatus) return;

    // 🚀 ASOSIY FILTR: Agar rasm hali yuklanish jarayonida bo'lsa va 'blob:' bo'lsa, 
    // uni backendga YUBORMAYMIZ (bo'sh massiv yuboramiz yoki kutamiz)
    const cleanedPhotos = currentPhotos.filter(
      (p) => p.file_url && !p.file_url.startsWith("blob:")
    );

    if (!checklist || checklist.length === 0) return;

    const allItems = checklist.flatMap((s) => s.items ?? []);
    const currentItem = allItems.find((item) => item.id === itemId);
    
    // Agar rasm majburiy bo'lsa va hali serverga yuklanib ulgurmagan bo'lsa, saqlashni to'xtatamiz
    if (currentItem?.requires_photo && cleanedPhotos.length === 0) {
      console.log("Rasm hali serverga yuklanmoqda, kutamiz...");
      return; 
    }

    try {
      await api.post(`/shift-checks/${id}/answers`, {
        answers: [
          {
            item_id: itemId,
            status: currentStatus,
            comment: currentComment,
            photos: cleanedPhotos, // 🚀 Tozalangan rasmlar ro'yxati ketadi
          },
        ],
      });
    } catch (err) {
      console.error(err);
    }
  },
  [id, checklist]
);


// Submit tugmasini bosishdan oldin tekshiruv
function submitShiftCheck() {
  const allQuestions = checklist.flatMap((section) => section.items ?? []);
  const totalItems = allQuestions.length;

  const answeredCount = allQuestions.filter((item) => {
    const ans = answersRef.current[item.id];
    return ans?.status && ans.status !== "";
  }).length;

  if (answeredCount < totalItems) {
    toast.error(
      `Вы ответили только на ${answeredCount} из ${totalItems} вопросов. Заполните все поля!`
    );
    return;
  }

  setConfirmOpen(true);
}

async function confirmSubmit() {
  setConfirmOpen(false);
  setSubmitting(true);
  try {
    await api.post(`/shift-checks/${id}/submit`);
    toast.success("Чек-лист успешно отправлен!");
    navigate("/dashboard");
  } catch (err) {
    console.error(err);
    if (err.response?.status === 404) {
      toast.error(
        "Ошибка 404: Не удалось отправить. Проверьте соответствие филиала чеклисту!"
      );
    } else {
      toast.error(
        err.response?.data?.detail || "Ошибка при отправке чеклиста"
      );
    }
  } finally {
    setSubmitting(false);
  }
}

  // ISO vaqtni O'zbekiston vaqtiga o'girish (ru-RU ishlatiladi — barcha brauzerlarda ishonchli)
const uzbFormattedDate = (() => {
  if (!shift?.started_at) return "";
  try {
    const date = new Date(shift.started_at);
    return date.toLocaleString("ru-RU", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "Asia/Tashkent",
    });
  } catch (_e) {
    return shift.started_at;
  }
})();

  const allQuestions = checklist.flatMap((section) => section.items ?? []);
  const totalItems = allQuestions.length;

  const answeredItems = allQuestions.filter((item) => {
    const ans = answers[item.id];
    return ans && ans.status !== undefined && ans.status !== null && ans.status !== "";
  }).length;

  const progressPercent =
    totalItems > 0 ? Math.round((answeredItems / totalItems) * 100) : 0;

  // --- RENDER ---

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-gray-900 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-gray-500 font-medium">
            Загрузка данных смены...
          </p>
        </div>
      </div>
    );
  }

  if (!shift) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-2xl text-center max-w-md">
          <p className="font-semibold text-lg mb-1">Данные не найдены</p>
          <p className="text-sm">{error || "Не удалось загрузить смену."}</p>
          <button
            onClick={loadData}
            className="mt-4 px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-xl hover:bg-red-700 transition"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  const isSubmitted = shift.status === "submitted";

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 text-gray-800">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Header — sticky */}
          <div className="sticky top-0 z-50 bg-white/95 backdrop-blur-md p-3 rounded-b-xl shadow-sm border-b">          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
            <div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => navigate(-1)}
                  className="flex items-center justify-center w-8 h-8 rounded-xl border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:text-black active:scale-95 transition-all shadow-sm shrink-0 cursor-pointer"
                  title="Назад"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2.5}
                    stroke="currentColor"
                    className="w-5 h-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
                    />
                  </svg>
                </button>

                <h1 className="text-lg font-bold text-gray-900">
                  Проверка смены №{shift.id}
                </h1>
              </div>

              <p className="text-sm text-gray-500 mt-1">
                Филиал:
                <span className="font-semibold text-gray-700">
                  {shift.branch?.name
                    ? `${shift.branch.name} (${shift.branch_id})`
                    : shift.branch_id}
                </span>
                {" | "}
                Начато:
                <span className="font-semibold text-gray-700">
                  {uzbFormattedDate}
                </span>
              </p>
            </div>

          {/* Progress bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="h-2 rounded-full transition-all duration-500"
                style={{
                  width: `${progressPercent}%`,
                  backgroundColor:
                    progressPercent === 100 ? "#10b981" : "#f59e0b",
                }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-1 text-right">
              {progressPercent}% завершено
            </p>
          </div>
        </div>
      </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm text-center font-medium">
            {error}
          </div>
        )}

        {/* Savollar */}
        <div className="space-y-6">
          {checklist.map((section) => (
            <div key={section.id} className="space-y-3">
              <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest px-1">
                {section.title_ru}
              </h2>

              {(section.items ?? []).map((item) => {
                const rawPhotoUrl =
                  answers[item.id]?.photos?.[0]?.file_url ?? null;
                const fullPhotoUrl = buildPhotoUrl(rawPhotoUrl);
                const itemAnswer = answers[item.id] ?? {};

                return (
                  <div
                    key={item.id}
                    className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 space-y-4"
                  >
                    <div className="flex justify-between items-start gap-4">
                      <span className="text-base font-semibold text-gray-900 leading-snug">
                        {item.title_ru}
                      </span>
                      {item.requires_photo && (
                        <span className="shrink-0 bg-red-50 text-red-600 text-xs px-2 py-0.5 rounded font-medium border border-red-100">
                          Фото обязательно
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start">
                      <div className="space-y-3">
                        <select
                          disabled={isSubmitted}
                          value={itemAnswer.status || ""}
                          onChange={(e) => {
                            const nextStatus = e.target.value;
                            handleAnswerChange(item.id, "status", nextStatus);
                            // forcedStatus beramiz — answersRef yangilanishini kutmaymiz
                            saveItemAnswer(item.id, nextStatus);
                          }}
                          className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl outline-none text-sm font-medium focus:border-gray-400 transition"
                        >
                          <option value="">Выберите статус</option>
                          <option value="yes">Да</option>
                          <option value="no">Нет</option>
                        </select>

                        <input
                          disabled={isSubmitted}
                          placeholder="Напишите комментарий..."
                          value={itemAnswer.comment || ""}
                          onChange={(e) =>
                            handleAnswerChange(
                              item.id,
                              "comment",
                              e.target.value
                            )
                          }
                          onBlur={() => saveItemAnswer(item.id)}
                          className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl outline-none text-sm focus:border-gray-400 transition"
                        />
                      </div>

                      <div className="space-y-3">
                        {/* FIX: Rasm mavjud bo'lsa "Yangilash", bo'lmasa "Yuklash" ko'rsatiladi */}
                        <label
                          className={`w-full flex items-center justify-center gap-2 py-2.5 border-2 border-dashed border-gray-200 rounded-xl text-sm font-medium transition ${
                            isSubmitted
                              ? "opacity-50 cursor-not-allowed"
                              : "cursor-pointer hover:bg-gray-50 hover:border-gray-300"
                          }`}
                        >
                          {fullPhotoUrl ? "🔄 Обновить фото" : "📸 Открыть камеру"}
                          <input
                            hidden
                            disabled={isSubmitted}
                            type="file"
                            accept="image/*"
                            capture="environment"
                            onChange={(e) => {
                              // FIX: input ni tozalaymiz, bir xil fayl qayta tanlanishiga ruxsat berish uchun
                              const file = e.target.files[0];
                              e.target.value = "";
                              uploadPhoto(item.id, file);
                            }}
                          />
                        </label>

                        {fullPhotoUrl && (
                          <div className="relative w-full h-28 rounded-xl overflow-hidden border bg-gray-50">
                            <img
                              src={fullPhotoUrl}
                              alt="Фото пункта"
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* Submit tugmasi */}
        {!isSubmitted && (
          <div className="pt-4 pb-10">
            <button
              onClick={submitShiftCheck}
              disabled={submitting}
              className="w-full py-4 bg-black text-white text-base font-bold rounded-2xl shadow-md hover:bg-gray-900 active:scale-[0.99] transition disabled:opacity-50"
            >
              {submitting ? "Отправка..." : "🏁 ЗАВЕРШИТЬ И ОТПРАВИТЬ ЧЕК-ЛИСТ"}
            </button>
          </div>
        )}
      </div>

      {/* Confirm modal */}
      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-900">
              Подтвердите отправку
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Вы уверены, что хотите завершить и отправить проверку?{" "}
              <span className="font-semibold text-gray-800">
                Редактирование станет невозможным.
              </span>
            </p>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setConfirmOpen(false)}
                className="flex-1 py-2.5 border border-gray-200 rounded-xl text-sm font-semibold text-gray-700 hover:bg-gray-50 transition"
              >
                Отмена
              </button>
              <button
                onClick={confirmSubmit}
                className="flex-1 py-2.5 bg-black text-white rounded-xl text-sm font-semibold hover:bg-gray-900 transition"
              >
                Отправить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );    
};  