// frontend/src/App.jsx
import { SignedIn, SignedOut, useUser } from "@clerk/clerk-react";
import "./App.css";

import Landing         from "./pages/Landing";
import DashboardLayout from "./layouts/DashboardLayout";
import AdminPanel      from "./pages/AdminPanel";
import AdminRoute      from "./components/AdminRoute";

function AppContent() {
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === "admin";

  // Si es admin → panel de administrador, si no → dashboard normal
  return isAdmin ? (
    <AdminRoute>
      <AdminPanel />
    </AdminRoute>
  ) : (
    <DashboardLayout />
  );
}

function App() {
  return (
    <>
      <SignedIn>
        <AppContent />
      </SignedIn>
      <SignedOut>
        <Landing />
      </SignedOut>
    </>
  );
}

export default App;