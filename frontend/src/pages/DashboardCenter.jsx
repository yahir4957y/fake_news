import { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { useAuth } from "@clerk/clerk-react";

export default function DashboardCenter({ history, setHistory }) {
  const { getToken } = useAuth();

  const [type, setType] = useState("texto");
  const [videoMode, setVideoMode] = useState("url");

  const [inputVal, setInputVal] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);

  const realCount = history.filter((h) => h.result.includes("Real")).length;
  const fakeCount = history.filter((h) => h.result.includes("Fake")).length;
  const chartData = [
    { name: "Real", value: realCount },
    { name: "Fake", value: fakeCount },
  ];

  const handleAnalyze = async () => {
    if (!inputVal && !file) return;

    setLoading(true);
    setProgress(10);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("tipo", type);

      if (type === "texto") {
        formData.append("texto", inputVal);
      } else if (type === "url") {
        formData.append("url", inputVal);
      } else if (type === "imagen") {
        formData.append("archivo", file);
      } else if (type === "video") {
        if (videoMode === "url") {
          formData.append("url", inputVal);
        } else {
          formData.append("archivo", file);
        }
      }

      setProgress(40);

      // Pedimos el token de sesión activo de Clerk
      const token = await getToken();

      // 🚨 ¡AQUÍ ESTABA EL ERROR! CORREGIDO A LA RUTA DEL ROUTER 🚨
      const response = await fetch("http://localhost:8000/api/analisis/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      setProgress(80);
      const data = await response.json();
      setProgress(100);

      if (response.ok) {
        const newRecord = {
          type,
          result: data.resultado === "Fake" ? "Fake ❌" : "Real 🟢",
          confidence: data.score_credibilidad || 0,
          date: new Date().toLocaleString(),
          details: data.detalles || "Sin detalles adicionales",
        };

        setResult(newRecord);
        setHistory([newRecord, ...history]);
      } else {
        alert("Error del servidor: " + (data.detail || "Error de validación"));
      }
    } catch (error) {
      console.error("Error al conectar:", error);
      alert("Error de conexión. ¿Está encendido el Backend (Uvicorn)?");
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  return (
    <main className="center-panel">
      <div className="panel-header">
        <h1>Análisis de Contenido</h1>
        <p style={{ color: "#64748b", fontSize: "0.9rem" }}>
          Ingresa los datos para verificación por IA
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="stats-wrapper">
          <div className="stat-box">
            <h4>Consultas Totales</h4>
            <p>{history.length}</p>
          </div>
          <div className="stat-box">
            <h4>Contenido Real</h4>
            <p style={{ color: "#4ade80" }}>{realCount}</p>
          </div>
          <div className="stat-box">
            <h4>Desinformación</h4>
            <p style={{ color: "#f87171" }}>{fakeCount}</p>
          </div>
        </div>

        <div className="chart-box">
          {history.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  dataKey="value"
                  paddingAngle={4}
                  stroke="none"
                >
                  <Cell fill="#22c55e" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#020617",
                    border: "1px solid #1e293b",
                    borderRadius: "8px",
                    color: "white",
                  }}
                  itemStyle={{ color: "white" }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "#475569", fontSize: "0.85rem" }}>
              Aún no hay datos
            </p>
          )}
        </div>
      </div>

      <div className="analysis-container">
        <div className="input-tabs">
          {["texto", "url", "imagen", "video"].map((t) => (
            <button
              key={t}
              className={`tab-btn ${type === t ? "active" : ""}`}
              onClick={() => {
                setType(t);
                setInputVal("");
                setFile(null);
                setResult(null);
              }}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>

        {type === "texto" && (
          <textarea
            className="input-field"
            rows="4"
            placeholder="Pega el artículo o texto sospechoso aquí..."
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
          />
        )}

        {type === "url" && (
          <input
            type="text"
            className="input-field"
            placeholder="https://ejemplo.com/noticia..."
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
          />
        )}

        {type === "imagen" && (
          <input
            type="file"
            accept="image/*"
            className="input-field"
            onChange={(e) => setFile(e.target.files[0])}
          />
        )}

        {type === "video" && (
          <div>
            <div className="sub-tabs">
              <button
                className={`sub-tab-btn ${videoMode === "url" ? "active" : ""}`}
                onClick={() => setVideoMode("url")}
              >
                Pegar Enlace
              </button>
              <button
                className={`sub-tab-btn ${videoMode === "file" ? "active" : ""}`}
                onClick={() => setVideoMode("file")}
              >
                Subir Archivo
              </button>
            </div>

            {videoMode === "url" ? (
              <input
                type="text"
                className="input-field"
                placeholder="Enlace de YouTube, TikTok, Twitter..."
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
              />
            ) : (
              <input
                type="file"
                accept="video/*"
                className="input-field"
                onChange={(e) => setFile(e.target.files[0])}
              />
            )}
          </div>
        )}

        <button
          className="btn-analyze"
          onClick={handleAnalyze}
          disabled={loading || (!inputVal && !file)}
        >
          {loading ? "Analizando patrones..." : "Iniciar Verificación"}
        </button>

        {loading && (
          <div className="progress-container">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}

        {result && (
          <div
            className={`result-box ${
              result.result.includes("Fake") ? "fake" : "real"
            }`}
          >
            {result.result} &nbsp;•&nbsp; Confianza de IA: {result.confidence}%
            {result.details && (
              <p style={{ fontSize: "0.8rem", marginTop: "5px", opacity: 0.9 }}>
                {result.details}
              </p>
            )}
          </div>
        )}
      </div>
    </main>
  );
}