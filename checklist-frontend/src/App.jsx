import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
// import ShiftChecksPage from "./pages/ShiftChecksPage";
import ShiftCheckDetailPage from "./pages/ShiftCheckDetailPage";
import ProtectedRoute from "./components/ProtectedRoute";
import ReportsPage from "./pages/ReportsPage";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin-dashboard"
          element={
            <ProtectedRoute>
              <AdminDashboardPage />
            </ProtectedRoute>
          }
        />

        {/* <Route
          path="/shift-checks"
          element={
            <ProtectedRoute>
              <ShiftChecksPage />
            </ProtectedRoute>
          }
        /> */}

        <Route
          path="/shift-checks/:id"
          element={
            <ProtectedRoute>
              <ShiftCheckDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}