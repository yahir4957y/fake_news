import { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { useAuth } from "@clerk/clerk-react";
import "./DashboardCenter.css";

// 🌟 IMPORTAMOS TUS COMPONENTES MODULARES
import SubidaImagen from "./SubidaImagen";
import InputTexto from "./InputTexto";
import InputUrl from "./InputUrl";

const LOADING_MESSAGES = [
  "Iniciando motores de Inteligencia Artificial...",
  "Analizando píxeles y metadatos ocultos...",
  "Cruzando información con bases de datos globales...",
  "Buscando patrones de desinformación...",
  "Casi listo, preparando tu veredicto final..."
];

export default function DashboardCenter({ history, setHistory }) {
  const { getToken } = useAuth();

  const [type, setType] = useState("texto");
  const [videoMode, setVideoMode] = useState("url");

  const [inputVal, setInputVal] = useState("");
  const [file, setFile] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [result, setResult] = useState(null);

  const realCount = history.filter((h) => h.result.includes("Real")).length;
  const fakeCount = history.filter((h) => h.result.includes("Fake")).length;
  const chartData = [
    { name: "Real", value: realCount },
    { name: "Fake", value: fakeCount },
  ];

  // 🔥 NUEVA FUNCIÓN: Limpia todos los estados sin recargar la página
  const handleNuevaConsulta = () => {
    setResult(null);
    setFeedback(null);
    setInputVal("");
    setFile(null);
  };

  const handleAnalyze = async () => {
    if (!inputVal && !file) {
      setFeedback({ type: "warning", message: "Ingresa un texto, enlace o archivo para comenzar." });
      return;
    }

    setLoading(true);
    setResult(null);
    setFeedback(null);
    
    let messageIndex = 0;
    setStatusText(LOADING_MESSAGES[0]);
    const messageInterval = setInterval(() => {
      messageIndex = (messageIndex + 1) % LOADING_MESSAGES.length;
      setStatusText(LOADING_MESSAGES[messageIndex]);
    }, 2200);

    try {
      setProgress(20);
      const formData = new FormData();
      formData.append("tipo", type);

      if (type === "texto") formData.append("texto", inputVal);
      else if (type === "url") formData.append("url", inputVal);
      else if (type === "imagen") formData.append("archivo", file);
      else if (type === "video") {
        videoMode === "url" ? formData.append("url", inputVal) : formData.append("archivo", file);
      }

      setProgress(40);
      const token = await getToken();

      setProgress(70);
      const response = await fetch("http://localhost:8000/api/analisis/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      setProgress(90);
      const data = await response.json();
      setProgress(100);

      if (response.ok) {
        const newRecord = {
          type,
          result: data.resultado === "Fake" ? "Fake ❌" : "Real 🟢",
          confidence: data.score_credibilidad || 0,
          date: new Date().toLocaleString(),
          details: data.detalles || "Sin detalles",
          recomendacion: data.recomendacion || "",
          fuentes: data.fuentes || [],
          context: data.context || null,
          sources: data.sources || []
        };

        setResult(newRecord);
        setHistory([newRecord, ...history]);
      } else {
        if (response.status === 429) {
          setFeedback({ 
            type: "warning", 
            message: `⏳ ${data.detail || "Sistema con alta demanda. Por favor, espera 60 segundos y vuelve a intentar."}` 
          });
        } else {
          setFeedback({ type: "error", message: data.detail || "Error al procesar el contenido." });
        }
      }
    } catch (error) {
      setFeedback({ type: "error", message: "🔌 Error de conexión. Verifica que el servidor backend esté en línea." });
    } finally {
      clearInterval(messageInterval);
      setTimeout(() => {
        setLoading(false);
        setProgress(0);
        setStatusText("");
      }, 1000);
    }
  };

  return (
    <main className="center-panel">
      <div className="panel-header">
        <h1>Análisis de Contenido</h1>
        <p className="panel-subtitle">Despliega el poder de la IA para detectar desinformación.</p>
      </div>

      <div className="dashboard-grid">
        <div className="stats-wrapper">
          <div className="stat-box"><h4>Consultas Totales</h4><p>{history.length}</p></div>
          <div className="stat-box"><h4>Contenido Real</h4><p className="text-real">{realCount}</p></div>
          <div className="stat-box"><h4>Desinformación</h4><p className="text-fake">{fakeCount}</p></div>
        </div>
        <div className="chart-box">
          {history.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={chartData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" stroke="none">
                  <Cell fill="#22c55e" /><Cell fill="#ef4444" />
                </Pie>
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", color: "white", borderRadius: "8px" }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-chart">Aún no hay datos</div>
          )}
        </div>
      </div>

      <div className="analysis-container">
        <div className="input-tabs">
          {["texto", "url", "imagen", "video"].map((t) => (
            <button
              key={t}
              className={`tab-btn ${type === t ? "active" : ""}`}
              onClick={() => { setType(t); setInputVal(""); setFile(null); setResult(null); setFeedback(null); }}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>

        <div className="input-area">
          {/* 🔥 USAMOS LOS NUEVOS COMPONENTES MODULARES 🔥 */}
          {type === "texto" && (
            <InputTexto 
              value={inputVal} 
              onChange={(e) => setInputVal(e.target.value)} 
            />
          )}
          
          {type === "url" && (
            <InputUrl 
              value={inputVal} 
              onChange={(e) => setInputVal(e.target.value)} 
            />
          )}
          
          {type === "imagen" && (
            <SubidaImagen 
              file={file} 
              setFile={setFile} 
            />
          )}
          
          {type === "video" && (
            <div style={{ width: "100%" }}>
              <div className="sub-tabs">
                <button className={`sub-tab-btn ${videoMode === "url" ? "active" : ""}`} onClick={() => setVideoMode("url")}>Enlace Web</button>
                <button className={`sub-tab-btn ${videoMode === "file" ? "active" : ""}`} onClick={() => setVideoMode("file")}>Subir Archivo</button>
              </div>
              {videoMode === "url" ? (
                <InputUrl 
                  value={inputVal} 
                  onChange={(e) => setInputVal(e.target.value)} 
                />
              ) : (
                <p style={{color: '#64748b', textAlign: 'center', padding: '20px 0'}}>Módulo de video en construcción...</p>
              )}
            </div>
          )}
        </div>

        {feedback && (
          <div className={`feedback-banner feedback-${feedback.type}`}>
            {feedback.message}
          </div>
        )}

        <button className="btn-analyze" onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analizando en curso..." : "Iniciar Verificación IA"}
        </button>

        {loading && (
          <div className="progress-wrapper">
            <div className="progress-text">
              <span>{statusText}</span>
              <span>{progress}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}

        {result && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div className={`result-container ${result.result.includes("Fake") ? "is-fake" : "is-real"}`}>
              <div className="result-header">
                <h3 className="result-title">{result.result}</h3>
                <span className="result-confidence">CONFIANZA: {result.confidence}%</span>
              </div>
              
              <p className="result-details">{result.details}</p>

              {result.fuentes && result.fuentes.length > 0 && (
                <div className="sources-container">
                  <h5 className="sources-title">🔗 Enlaces de Fact-Checking:</h5>
                  <div className="sources-list">
                    {result.fuentes.map((fuente, idx) => {
                      const isObject = typeof fuente === 'object';
                      const nombre = isObject ? fuente.nombre : fuente;
                      const url = isObject ? fuente.url : `https://www.google.com/search?q=${encodeURIComponent(fuente)}`;

                      return (
                        <a key={idx} href={url} target="_blank" rel="noopener noreferrer" className="source-link">
                          <span className="source-icon">🌐</span> {nombre}
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}
              {result.context && (
                <div style={{ marginTop: "12px", padding: "10px", backgroundColor: "rgba(0,0,0,0.2)", borderRadius: "6px" }}>
                  <p style={{ fontSize: "0.85rem", opacity: 0.9, margin: 0 }}>
                    <strong>Contexto:</strong> {result.context}
                  </p>
                </div>
              )}
              {result.sources && result.sources.length > 0 && (
                <div style={{ marginTop: "15px" }}>
                  <strong style={{ fontSize: "0.85rem", display: "block", marginBottom: "5px" }}>Fuentes para Verificar:</strong>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                    {result.sources.map((src, idx) => (
                      <a 
                        key={idx} 
                        href={src.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{
                          fontSize: "0.8rem",
                          padding: "5px 10px",
                          backgroundColor: "rgba(255,255,255,0.1)",
                          color: "white",
                          textDecoration: "none",
                          borderRadius: "4px",
                          border: "1px solid rgba(255,255,255,0.2)",
                          transition: "all 0.2s"
                        }}
                      >
                        🔗 {src.nombre}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 🔥 BOTÓN PARA NUEVA CONSULTA 🔥 */}
            <div style={{ display: "flex", justifyContent: "center", marginTop: "10px" }}>
              <button 
                onClick={handleNuevaConsulta}
                style={{
                  backgroundColor: "#3b82f6",
                  color: "white",
                  padding: "12px 30px",
                  borderRadius: "8px",
                  fontWeight: "bold",
                  border: "none",
                  cursor: "pointer",
                  fontSize: "1rem",
                  boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
                  transition: "background 0.2s"
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = "#2563eb"}
                onMouseOut={(e) => e.target.style.backgroundColor = "#3b82f6"}
              >
                🔄 Realizar Nueva Consulta
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}