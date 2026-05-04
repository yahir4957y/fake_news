import { useState, useRef } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { useAuth } from "@clerk/clerk-react";
import "./DashboardCenter.css"; // 🌟 IMPORTAMOS EL NUEVO CSS

const LOADING_MESSAGES = [
  "Iniciando motores de Inteligencia Artificial...",
  "Analizando píxeles y metadatos ocultos...",
  "Cruzando información con bases de datos globales...",
  "Buscando patrones de desinformación...",
  "Casi listo, preparando tu veredicto final..."
];

export default function DashboardCenter({ history, setHistory }) {
  const { getToken } = useAuth();
  const fileInputRef = useRef(null);

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

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
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
          fuentes: data.fuentes || []
        };

        setResult(newRecord);
        setHistory([newRecord, ...history]);
      } else {
        // 🛡️ AQUÍ CAPTURAMOS EL ERROR 429 DE TOKENS (Rate Limit)
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

  const UploadZone = ({ accept }) => (
    <div 
      className={`upload-zone ${file ? 'active' : ''}`}
      onClick={() => fileInputRef.current.click()}
    >
      <input type="file" accept={accept} style={{ display: "none" }} ref={fileInputRef} onChange={handleFileChange} />
      <div className="upload-icon">{file ? "📄" : "📁"}</div>
      <h4 className="upload-title">{file ? file.name : "Haz clic o arrastra tu archivo aquí"}</h4>
      <p className="upload-subtitle">
        {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : `Formatos soportados: ${accept}`}
      </p>
    </div>
  );

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
          {type === "texto" && <textarea className="input-field" rows="5" placeholder="Pega el artículo o fragmento aquí..." value={inputVal} onChange={(e) => setInputVal(e.target.value)} />}
          {type === "url" && <input type="text" className="input-field" placeholder="Ej: https://x.com/noticia-sospechosa" value={inputVal} onChange={(e) => setInputVal(e.target.value)} />}
          {type === "imagen" && <UploadZone accept="image/*" />}
          {type === "video" && (
            <div style={{ width: "100%" }}>
              <div className="sub-tabs">
                <button className={`sub-tab-btn ${videoMode === "url" ? "active" : ""}`} onClick={() => setVideoMode("url")}>Enlace Web</button>
                <button className={`sub-tab-btn ${videoMode === "file" ? "active" : ""}`} onClick={() => setVideoMode("file")}>Subir Archivo</button>
              </div>
              {videoMode === "url" ? (
                <input type="text" className="input-field" placeholder="Enlace de YouTube, TikTok..." value={inputVal} onChange={(e) => setInputVal(e.target.value)} />
              ) : (
                <UploadZone accept="video/*" />
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
          </div>
        )}
      </div>
    </main>
  );
}