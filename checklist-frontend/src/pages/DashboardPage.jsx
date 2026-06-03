import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const navigate = useNavigate();

   async function startShiftCheck() {
    try {
      // LocalStorage-dan tizimga kirgan foydalanuvchi ma'lumotlarini olamiz
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      
      // Agar foydalanuvchida branch_id bo'lmasa, xatolik chiqaramiz
      if (!user.branch_id) {
        toast.error("Ошибка: У вашего пользователя не указан филиал (Branch ID)");
        return;
      }

      const res = await api.post("/shift-checks/start", {
        shift_type: "day",
        branch_id: parseInt(user.branch_id), // Albatta raqam (Integer) formatida yuboramiz!
      });

      toast.success("Проверка начата");
      navigate(`/shift-checks/${res.data.id}`);
    } catch (err) {
      console.log(err);
      toast.error(
        err.response?.data?.detail || "Ошибка запуска проверки (400)"
      );
    }
  }


  function logout() {
    localStorage.removeItem("access_token");
    navigate("/");
  }
  const userData = localStorage.getItem("user");
  const user = userData && userData !== "undefined"
    ? JSON.parse(userData)
    : null;

  return (
    <div
      style={{
        padding: 24,
        maxWidth: 520,
        margin: "0 auto",
      }}
    >
      {/* <h1 style={{ marginBottom: 8 }}>MAXWAY</h1> */}
      <h1>
        <b>MAXWAY</b>
      </h1>
      <p>
        <b>Пользователь:</b> {user?.full_name}
      </p>

      <p>
        <b>Роль:</b> {user?.role}
      </p>

      <p>
        <b>Филиал:</b> {user?.branch_name}
      </p>

      {/* <p style={{ color: "#666", marginBottom: 24 }}>
        Система чек-листов смены
      </p> */}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        <button
          onClick={startShiftCheck}
          style={{
            padding: "16px 18px",
            borderRadius: 12,
            border: "none",
            background: "#729c87",
            color: "#fff",
            fontSize: 16,
            cursor: "pointer",
          }}
        >
          Начать дневную проверку
        </button>

        <button
          onClick={() => navigate("/reports")}
          style={{
            padding: "16px 18px",
            borderRadius: 12,
            border: "1px solid #79a0e4",
            background: "#9bb7d1",
            fontSize: 16,
            cursor: "pointer",
          }}
        >
          Список проверок
        </button>

        {/* <button
          onClick={() => navigate("/reports")}
          style={{
            padding: "16px 18px",
            borderRadius: 12,
            border: "1px solid #ddd",
            background: "#dce6a4",
            fontSize: 16,
            cursor: "pointer",
          }}
        >
          Отчеты
        </button> */}

        <button
          onClick={logout}
          style={{
            padding: "16px 18px",
            borderRadius: 12,
            border: "1px solid #f1c0c0",
            background: "#fff5f5",
            color: "#c00",
            fontSize: 16,
            cursor: "pointer",
          }}
        >
          Выйти
        </button>
      </div>
    </div>
  );
}
