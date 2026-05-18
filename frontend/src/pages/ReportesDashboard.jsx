import { useState } from "react";
import { useReports } from "../hook/useReports";
import { ReportesFilters } from "../components/ReportesFilters";
import { ReportesTable } from "../components/ReportesTable";
import "../styles/ReportesDashboard.css";

export default function ReportesDashboard({ onBack }) {
  const { analisis, loading, error } = useReports();
  const [filtro, setFiltro] = useState("");
  const [tipoFiltro, setTipoFiltro] = useState("");

  if (loading) {
    return (
      <div className="reportes-dashboard">
        <div className="loading-container">
          <div className="spinner-large"></div>
          <p>Cargando análisis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reportes-dashboard">
        <div className="error-container">
          <p className="error-message">❌ Error: {error}</p>
          <p className="error-detail">No se pudieron cargar los análisis. Intenta más tarde.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="reportes-dashboard">
      <header className="reportes-header">
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <button
            onClick={onBack}
            style={{
              background: "#1e293b", border: "1px solid #334155", color: "#94a3b8",
              padding: "0.4rem 0.9rem", borderRadius: "8px", cursor: "pointer",
              fontSize: "0.85rem"
            }}
          >
            ← Volver al Dashboard
          </button>
          <h1>📊 Mis Reportes</h1>
        </div>
        <p className="reportes-subtitle">
          Total de análisis: <strong>{analisis.length}</strong>
        </p>
      </header>

      <div className="reportes-content">
        <ReportesFilters
          filtro={filtro}
          setFiltro={setFiltro}
          tipoFiltro={tipoFiltro}
          setTipoFiltro={setTipoFiltro}
        />

        <ReportesTable
          analisis={analisis}
          filtro={filtro}
          tipoFiltro={tipoFiltro}
        />
      </div>
    </div>
  );
}
