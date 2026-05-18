import { useState } from "react";
import { useExport } from "../hook/useExport";
import "../styles/ReportesDashboard.css";

export function ExportButton({ verificacionId }) {
  const { descargarReporte } = useExport();
  const [descargando, setDescargando] = useState(false);
  const [formato, setFormato] = useState(null);
  const [showMenu, setShowMenu] = useState(false);

  const handleDescargar = async (fmt) => {
    setDescargando(true);
    setFormato(fmt);
    try {
      await descargarReporte(verificacionId, fmt);
      setShowMenu(false);
    } finally {
      setDescargando(false);
      setFormato(null);
    }
  };

  return (
    <div className="export-button-container">
      <button
        className="export-button"
        onClick={() => setShowMenu(!showMenu)}
        disabled={descargando}
      >
        {descargando && formato ? (
          <>
            <span className="spinner"></span>
            Descargando {formato.toUpperCase()}...
          </>
        ) : (
          <>
            📥 Exportar
          </>
        )}
      </button>

      {showMenu && !descargando && (
        <div className="export-menu">
          <button
            className="export-option pdf"
            onClick={() => handleDescargar("pdf")}
          >
            <span className="icon">📄</span>
            <span>Descargar PDF</span>
          </button>
          <button
            className="export-option csv"
            onClick={() => handleDescargar("csv")}
          >
            <span className="icon">📊</span>
            <span>Descargar CSV</span>
          </button>
        </div>
      )}
    </div>
  );
}
