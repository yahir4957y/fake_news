import { useState, useEffect } from "react";
import { useUser, useAuth, UserButton } from "@clerk/clerk-react";
import Sidebar from "../components/Sidebar.jsx";
import DashboardCenter from "../pages/DashboardCenter.jsx";
import ReportesDashboard from "../pages/ReportesDashboard.jsx";
import TokenDashboard from "../pages/TokenDashboard.jsx";
import "./DashboardLayout.css"; 

export default function DashboardLayout() {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
  
  const [history, setHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [analisisSeleccionado, setAnalisisSeleccionado] = useState(null);
  const [activeView, setActiveView] = useState("dashboard");

  useEffect(() => {
    const fetchHistorial = async () => {
      try {
        setIsLoadingHistory(true);
        const token = await getToken();
        const response = await fetch("http://localhost:8000/api/analisis/historial", {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.ok) {
          const data = await response.json();
          setHistory(data);
        }
      } catch (error) {
        console.error("Error cargando historial de BD:", error);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    if (isLoaded && user) {
      fetchHistorial();
    }
  }, [isLoaded, user, getToken]);

  const saveHistory = (newHistory) => {
    setHistory(newHistory);
  };

  const handleAbrirModal = (item) => {
    setAnalisisSeleccionado(item);
    setIsModalOpen(true);
  };

  const handleCerrarModal = () => {
    setIsModalOpen(false);
    setAnalisisSeleccionado(null);
  };

  if (!isLoaded) {
    return (
      <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center", backgroundColor: "#0f172a", color: "#3b82f6" }}>
        <h2>Iniciando sistema...</h2>
      </div>
    );
  }

  return (
    <div className="dashboard-wrapper">
      <header className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem', backgroundColor: '#020617', borderBottom: '1px solid #1e293b' }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
          <h2 className="logo" style={{ fontSize: "1.4rem", margin: 0, color: "white" }}>
            FakeNews<span style={{ color: "#3b82f6" }}>AI</span>
          </h2>

          <nav className="dashboard-nav">
            <button
              className={`dashboard-nav-btn ${activeView === "dashboard" ? "active" : ""}`}
              onClick={() => setActiveView("dashboard")}
            >
              Dashboard
            </button>
            <button
              className={`dashboard-nav-btn ${activeView === "reportes" ? "active" : ""}`}
              onClick={() => setActiveView("reportes")}
            >
              Reportes
            </button>
            <button
              className={`dashboard-nav-btn ${activeView === "tokens" ? "active" : ""}`}
              onClick={() => setActiveView("tokens")}
            >
              Tokens
            </button>
          </nav>
        </div>
        
        <div className="user-section" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="user-info" style={{ textAlign: 'right', display: 'flex', flexDirection: 'column' }}>
            <span className="user-name" style={{ fontSize: '0.95rem', fontWeight: '600', color: '#f8fafc' }}>
              {user?.fullName || "Analista IA"}
            </span>
            <span className="user-email" style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              {user?.primaryEmailAddress?.emailAddress}
            </span>
          </div>
          <UserButton 
            afterSignOutUrl="/" 
            appearance={{ elements: { avatarBox: { width: 42, height: 42, border: "2px solid #1e293b" } } }} 
          />
        </div>
      </header>

      {activeView === "dashboard" && (
        <main className="dashboard-main" style={{ display: 'flex', height: 'calc(100vh - 75px)' }}>
          <Sidebar 
            history={history} 
            onAbrirModal={handleAbrirModal} 
            loading={isLoadingHistory} 
          />
          <DashboardCenter 
            history={history} 
            setHistory={saveHistory} 
            loadingHistory={isLoadingHistory} 
          />
        </main>
      )}

      {activeView === "reportes" && (
        <main className="dashboard-main dashboard-main-full">
          <ReportesDashboard onBack={() => setActiveView("dashboard")} />
        </main>
      )}

      {activeView === "tokens" && (
        <main className="dashboard-main dashboard-main-full">
          <TokenDashboard onBack={() => setActiveView("dashboard")} />
        </main>
      )}

      {isModalOpen && analisisSeleccionado && (
        <div className="modal-overlay" onClick={handleCerrarModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            
            <button className="modal-close" onClick={handleCerrarModal}>
              ✖
            </button>

            <h2 style={{ margin: "0 0 5px 0", color: "#f8fafc" }}>
              Resumen del Análisis
            </h2>
            <p style={{ margin: "0", color: "#94a3b8", fontSize: "0.9rem" }}>
              Analizado el {analisisSeleccionado.date}
            </p>

            <div className="modal-info">
              
              <div className="modal-row-container">
                <div>
                  <span style={{ color: "#94a3b8", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "1px" }}>Resultado Final</span>
                  <span className={analisisSeleccionado.result.includes('Real') ? 'badge-real' : 'badge-fake'}>
                    {analisisSeleccionado.result}
                  </span>
                </div>
                
                <div style={{ alignItems: "flex-end" }}>
                  <span style={{ color: "#94a3b8", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "1px" }}>Nivel de Certeza</span>
                  <span style={{ fontSize: "1.8rem", fontWeight: "bold", color: "#f8fafc" }}>
                    {analisisSeleccionado.confidence}%
                  </span>
                </div>
              </div>

              <div className="modal-details">
                <h3 style={{ margin: "0 0 10px 0", color: "#e2e8f0", fontSize: "1.1rem" }}>Detalles Técnicos y Justificación:</h3>
                <p>
                  {analisisSeleccionado.details || "El análisis se completó sin detalles adicionales."}
                </p>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}
