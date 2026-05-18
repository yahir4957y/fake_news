import "../styles/ReportesDashboard.css";

export function ReportesFilters({ filtro, setFiltro, tipoFiltro, setTipoFiltro }) {
  return (
    <div className="reportes-filters">
      <div className="filter-group">
        <label htmlFor="filtro-tipo">Filtrar por tipo:</label>
        <select
          id="filtro-tipo"
          value={tipoFiltro}
          onChange={(e) => setTipoFiltro(e.target.value)}
          className="filter-select"
        >
          <option value="">Todos</option>
          <option value="texto">Texto</option>
          <option value="imagen">Imagen</option>
          <option value="video">Video</option>
          <option value="url">URL</option>
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="filtro-resultado">Filtrar por resultado:</label>
        <select
          value={filtro}
          onChange={(e) => setFiltro(e.target.value)}
          className="filter-select"
        >
          <option value="">Todos</option>
          <option value="Real">Real</option>
          <option value="Fake">Fake</option>
        </select>
      </div>

      <div className="filter-group">
        <button
          className="filter-reset"
          onClick={() => {
            setFiltro("");
            setTipoFiltro("");
          }}
        >
          ↺ Limpiar filtros
        </button>
      </div>
    </div>
  );
}
