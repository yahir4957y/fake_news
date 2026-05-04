import { useState, useEffect } from "react";
import { useUser, UserButton } from "@clerk/clerk-react";
import Sidebar from "../components/Sidebar.jsx";
import DashboardCenter from "../pages/DashboardCenter.jsx";
import "./DashboardLayout.css";

export default function DashboardLayout() {
  // 1. Extraemos isLoaded para evitar renderizados prematuros
  const { user, isLoaded } = useUser();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // 2. Try-Catch protector para leer el almacenamiento local
    try {
      const data = JSON.parse(localStorage.getItem("history")) || [];
      setHistory(data);
    } catch (error) {
      console.error("Error leyendo el historial:", error);
      setHistory([]);
    }
  }, []);

  const saveHistory = (newHistory) => {
    localStorage.setItem("history", JSON.stringify(newHistory));
    setHistory(newHistory);
  };

  // 3. Pantalla de carga suave mientras Clerk verifica la sesión
  if (!isLoaded) {
    return (
      <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center", backgroundColor: "#0f172a", color: "#3b82f6" }}>
        <h2>Iniciando sistema...</h2>
      </div>
    );
  }

  return (
    <div className="dashboard-wrapper">
      {/* TOPBAR PROFESIONAL */}
      <header className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem', backgroundColor: '#020617', borderBottom: '1px solid #1e293b' }}>
        <h2 className="logo" style={{ fontSize: "1.4rem", margin: 0, color: "white" }}>
          FakeNews<span style={{ color: "#3b82f6" }}>AI</span>
        </h2>
        
        <div className="user-section" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="user-info" style={{ textAlign: 'right', display: 'flex', flexDirection: 'column' }}>
            <span className="user-name" style={{ fontSize: '0.95rem', fontWeight: '600', color: '#f8fafc' }}>
              {user?.fullName || "Analista IA"}
            </span>
            <span className="user-email" style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              {user?.primaryEmailAddress?.emailAddress}
            </span>
          </div>
          
          {/* Avatar de Google con menú de perfil y cierre de sesión integrado */}
          <UserButton 
            afterSignOutUrl="/" 
            appearance={{ 
              elements: { avatarBox: { width: 42, height: 42, border: "2px solid #1e293b" } } 
            }} 
          />
        </div>
      </header>

      {/* ÁREA PRINCIPAL */}
      <main className="dashboard-main" style={{ display: 'flex', height: 'calc(100vh - 75px)' }}>
        <Sidebar history={history} />
        <DashboardCenter history={history} setHistory={saveHistory} />
      </main>
    </div>
  );
}