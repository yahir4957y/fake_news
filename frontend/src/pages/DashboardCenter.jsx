import { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { useAuth } from "@clerk/clerk-react";
import "./DashboardCenter.css";

import SubidaImagen from "./SubidaImagen";
import InputTexto from "./InputTexto";
import InputUrl from "./InputUrl";
import ModuloVideo from "./ModuloVideo";

const LOADING_MESSAGES = [
  "Iniciando motores de Inteligencia Artificial...",
  "Analizando píxeles y metadatos ocultos...",
  "Cruzando información con bases de datos globales...",
  "Buscando patrones de desinformación...",
  "Casi listo, preparando tu veredicto final..."
];

export default function DashboardCenter({ history, setHistory, loadingHistory }) {
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

  const realCount = history.filter(h => h.result.includes("Real")).length;
  const fakeCount = history.filter(h => h.result.includes("Fake")).length;
  
  const pieData = [
    { name: "Real", value: realCount },
    { name: "Fake", value: fakeCount }
  ];

  const typeData = [
    { name: "Texto", cant: history.filter(h => h.type === "texto").length },
    { name: "URL", cant: history.filter(h => h.type === "url").length },
    { name: "Imagen", cant: history.filter(h => h.type === "imagen").length },
    { name: "Video", cant: history.filter(h => h.type === "video").length },
  ];

  const formatDetails = (details) => {
    if (!details) return [];
    return String(details)
      .split(/\n+/)
      .map((paragraph) => paragraph.trim())
      .filter(Boolean);
  };

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
      let token;
      try {
        token = await getToken();
      } catch (authError) {
        console.error("Error obteniendo token de Clerk:", authError);
        setFeedback({
          type: "error",
          message: "No se pudo validar tu sesión con Clerk. Revisa que estés entrando por http://localhost:5173 y que el navegador no esté bloqueando Clerk."
        });
        return;
      }

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
          result: (data.resultado === "Real" || data.resultado === "verificado") ? "Real 🟢" : "Fake ❌",
          confidence: data.score_credibilidad || 0,
          date: new Date().toLocaleString('es-BO'),
          nivelRiesgo: data.nivel_riesgo || data.nivel_credibilidad || "",
          veredictoCorto: data.veredicto_corto || "",
          analisisContenido: data.analisis_contenido || "",
          indicadores: Array.isArray(data.indicadores) ? data.indicadores : [],
          contextoFactual: data.contexto_factual || "",
          tecnicasManipulacion: Array.isArray(data.tecnicas_manipulacion) ? data.tecnicas_manipulacion : [],
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
    } catch {
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
        <p className="panel-subtitle">Historial sincronizado con Supabase Cloud</p>
      </div>

      {loadingHistory ? (
        <div className="loading-history-container">
          <div className="spinner"></div>
          <p>Sincronizando con la base de datos...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="empty-state">
          <h3>🚀 ¡Bienvenido, Analista!</h3>
          <p>Tu historial está vacío. Realiza tu primer análisis abajo para empezar a recolectar datos.</p>
        </div>
      ) : (
        <div className="charts-container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          
          <div className="stats-wrapper" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div className="stat-box"><h4>Consultas Totales</h4><p>{history.length}</p></div>
            <div className="stat-box"><h4>Contenido Real</h4><p className="text-real">{realCount}</p></div>
            <div className="stat-box"><h4>Desinformación</h4><p className="text-fake">{fakeCount}</p></div>
          </div>

          {/* Gráfico Circular */}
          <div className="chart-box">
             <h4>Distribución de Veracidad</h4>
             {/* 🔥 Cambiamos a height="100%" y le damos un minHeight */}
             <div style={{ width: '100%', height: '250px' }}>
               <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} innerRadius={60} outerRadius={85} dataKey="value" stroke="none">
                      <Cell fill="#22c55e" /><Cell fill="#ef4444" />
                    </Pie>
                    <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", color: "white", borderRadius: "8px" }} />
                  </PieChart>
               </ResponsiveContainer>
             </div>
          </div>

          {/* Gráfico de Barras */}
          <div className="chart-box">
             <h4>Tipos de Contenido Analizado</h4>
             {/* 🔥 Igual aquí, contenedor fijo para que Recharts se expanda bonito */}
             <div style={{ width: '100%', height: '250px' }}>
               <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={typeData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={13} tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={13} tickLine={false} axisLine={false} allowDecimals={false} />
                    <Tooltip 
                      cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }} 
                      contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "8px" }}
                    />
                    <Bar dataKey="cant" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={40} />
                  </BarChart>
               </ResponsiveContainer>
             </div>
          </div>

        </div>
      )}

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
          {type === "texto" && <InputTexto value={inputVal} onChange={(e) => setInputVal(e.target.value)} />}
          {type === "url" && <InputUrl value={inputVal} onChange={(e) => setInputVal(e.target.value)} />}
          {type === "imagen" && <SubidaImagen file={file} setFile={setFile} />}
          {type === "video" && (
            <ModuloVideo 
              inputVal={inputVal} 
              setInputVal={setInputVal} 
              file={file} 
              setFile={setFile} 
              videoMode={videoMode}
              setVideoMode={setVideoMode}
            />
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
                <div>
                  <span className="result-kicker">Veredicto del análisis</span>
                  <h3 className="result-title">{result.result}</h3>
                </div>
                <div className="result-score-card">
                  <span>{result.confidence}%</span>
                  <small>{result.nivelRiesgo || "Confianza"}</small>
                </div>
              </div>

              {result.veredictoCorto && (
                <p className="result-verdict">{result.veredictoCorto}</p>
              )}

              <div className="result-grid">
                {result.analisisContenido && (
                  <section className="result-section">
                    <h4>Qué afirma el contenido</h4>
                    <p>{result.analisisContenido}</p>
                  </section>
                )}

                {result.contextoFactual && (
                  <section className="result-section">
                    <h4>Contexto factual</h4>
                    <p>{result.contextoFactual}</p>
                  </section>
                )}
              </div>

              {result.indicadores.length > 0 && (
                <section className="result-section">
                  <h4>Indicadores detectados</h4>
                  <div className="indicator-list">
                    {result.indicadores.map((indicador, idx) => (
                      <div key={idx} className={`indicator-item ${indicador.tipo || "neutro"}`}>
                        <span>{indicador.tipo || "neutro"}</span>
                        <p>{indicador.descripcion || indicador}</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {result.tecnicasManipulacion.length > 0 && (
                <section className="result-section">
                  <h4>Técnicas de manipulación</h4>
                  <div className="technique-list">
                    {result.tecnicasManipulacion.map((tecnica, idx) => (
                      <span key={idx}>{tecnica}</span>
                    ))}
                  </div>
                </section>
              )}

              <section className="result-section">
                <h4>Análisis técnico</h4>
                <div className="result-details">
                  {formatDetails(result.details).map((paragraph, idx) => (
                    <p key={idx}>{paragraph}</p>
                  ))}
                </div>
              </section>

              {result.recomendacion && (
                <section className="result-section recommendation">
                  <h4>Recomendación</h4>
                  <p>{result.recomendacion}</p>
                </section>
              )}

              {result.fuentes && result.fuentes.length > 0 && (
                <div className="sources-container">
                  <h5 className="sources-title">Enlaces de fact-checking</h5>
                  <div className="sources-list">
                    {result.fuentes.map((fuente, idx) => {
                      const isObject = typeof fuente === 'object';
                      const nombre = isObject ? fuente.nombre : fuente;
                      const url = isObject ? fuente.url : `https://www.google.com/search?q=${encodeURIComponent(fuente)}`;

                      return (
                        <a key={idx} href={url} target="_blank" rel="noopener noreferrer" className="source-link">
                          <span className="source-icon">↗</span> {nombre}
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

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
