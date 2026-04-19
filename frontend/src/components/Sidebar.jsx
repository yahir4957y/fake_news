import { useState } from "react";

export default function Sidebar({ history }) {
  const [filter, setFilter] = useState("all");

  const filteredHistory = history.filter(item => {
    if (filter === "real") return item.result.includes("Real");
    if (filter === "fake") return item.result.includes("Fake");
    return true;
  });

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3>Historial de Análisis</h3>
        <div className="filter-group">
          <button className={`filter-btn ${filter === "all" ? "active" : ""}`} onClick={() => setFilter("all")}>Todos</button>
          <button className={`filter-btn ${filter === "real" ? "active" : ""}`} onClick={() => setFilter("real")}>Reales</button>
          <button className={`filter-btn ${filter === "fake" ? "active" : ""}`} onClick={() => setFilter("fake")}>Fake</button>
        </div>
      </div>

      <div className="history-list">
        {filteredHistory.length === 0 && <p style={{color: "#64748b", fontSize: "0.85rem"}}>No hay verificaciones recientes.</p>}
        
        {filteredHistory.map((item, i) => (
          <div key={i} className={`history-card ${item.result.includes("Fake") ? "fake" : "real"}`}>
            <div style={{display: "flex", justifyContent: "space-between", marginBottom: "8px"}}>
              <strong style={{color: "#cbd5e1", textTransform: "uppercase", fontSize: "0.7rem", letterSpacing: "0.5px"}}>{item.type}</strong>
              <small style={{color: "#64748b", fontSize: "0.7rem"}}>{item.confidence}% certidumbre</small>
            </div>
            <p style={{margin: "0 0 5px 0", fontWeight: "600", color: "white", fontSize: "0.9rem"}}>{item.result}</p>
            <small style={{color: "#475569", fontSize: "0.7rem"}}>{item.date}</small>
          </div>
        ))}
      </div>
    </aside>
  );
}