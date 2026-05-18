import { ExportButton } from "./ExportButton";
import "../styles/ReportesDashboard.css";

export function ReportesTable({ analisis, filtro, tipoFiltro }) {
  // Filtrar análisis
  const analisisFiltrado = analisis.filter((item) => {
    const matchResultado = filtro === "" || item.resultado.includes(filtro);
    const matchTipo = tipoFiltro === "" || item.contenido_tipo === tipoFiltro;
    return matchResultado && matchTipo;
  });

  if (analisisFiltrado.length === 0) {
    return (
      <div className="tabla-vacia">
        <p>📭 No hay análisis que coincidan con los filtros seleccionados</p>
      </div>
    );
  }

  return (
    <div className="reportes-table-container">
      <table className="reportes-table">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Preview</th>
            <th>Resultado</th>
            <th>Confianza</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {analisisFiltrado.map((item) => (
            <tr key={item.verificacion_id} className="tabla-fila">
              <td className="tipo-celda">
                <span className="tipo-badge">{item.contenido_tipo.toUpperCase()}</span>
              </td>
              <td className="preview-celda" title={item.contenido_preview}>
                {item.contenido_preview.length > 50
                  ? item.contenido_preview.substring(0, 50) + "..."
                  : item.contenido_preview}
              </td>
              <td className="resultado-celda">
                <span
                  className={`resultado-badge ${
                    item.resultado.includes("Real") ? "real" : "fake"
                  }`}
                >
                  {item.resultado.includes("Real") ? "✓ Real" : "✗ Fake"}
                </span>
              </td>
              <td className="confianza-celda">
                <div className="confianza-bar">
                  <div
                    className="confianza-fill"
                    style={{
                      width: `${item.score_credibilidad}%`,
                      backgroundColor:
                        item.score_credibilidad > 70
                          ? "#22c55e"
                          : item.score_credibilidad > 40
                          ? "#eab308"
                          : "#ef4444",
                    }}
                  ></div>
                </div>
                <span className="confianza-texto">
                  {item.score_credibilidad.toFixed(0)}%
                </span>
              </td>
              <td className="fecha-celda">
                {new Date(item.fecha).toLocaleDateString("es-ES", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </td>
              <td className="acciones-celda">
                <ExportButton
                  verificacionId={item.verificacion_id}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="tabla-info">
        Mostrando {analisisFiltrado.length} de {analisis.length} análisis
      </div>
    </div>
  );
}
