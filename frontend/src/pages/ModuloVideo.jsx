import { useRef, useState } from "react";
import InputUrl from "./InputUrl";

export default function ModuloVideo({ inputVal, setInputVal, file, setFile, videoMode, setVideoMode }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type.startsWith("video/")) {
        if (droppedFile.size > 50 * 1024 * 1024) {
          alert("El video es muy pesado. Máximo 50MB para esta fase de pruebas.");
          return;
        }
        setFile(droppedFile);
      } else {
        alert("Por favor, sube solo archivos de video (MP4, WEBM, MOV).");
      }
    }
  };

  return (
    <div style={{ width: "100%", animation: "modalFadeIn 0.3s ease-out" }}>
      <div className="sub-tabs" style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
        <button 
          className={`sub-tab-btn ${videoMode === "url" ? "active" : ""}`} 
          onClick={() => { setVideoMode("url"); setFile(null); }}
          style={{ flex: 1, padding: "10px", borderRadius: "8px", border: "1px solid #334155", backgroundColor: videoMode === "url" ? "#3b82f6" : "transparent", color: "white", cursor: "pointer", transition: "all 0.2s" }}
        >
          🌐 Enlace Web
        </button>
        <button 
          className={`sub-tab-btn ${videoMode === "file" ? "active" : ""}`} 
          onClick={() => { setVideoMode("file"); setInputVal(""); }}
          style={{ flex: 1, padding: "10px", borderRadius: "8px", border: "1px solid #334155", backgroundColor: videoMode === "file" ? "#3b82f6" : "transparent", color: "white", cursor: "pointer", transition: "all 0.2s" }}
        >
          📁 Subir Archivo
        </button>
      </div>

      {videoMode === "url" ? (
        <div className="video-url-mode">
          <InputUrl value={inputVal} onChange={(e) => setInputVal(e.target.value)} />
          <p style={{ color: "#64748b", fontSize: "0.8rem", marginTop: "8px", paddingLeft: "4px" }}>
            * Pega enlaces de YouTube Shorts, TikToks o Twitter/X.
          </p>
        </div>
      ) : (
        <div 
          className="video-file-mode"
          onClick={() => fileInputRef.current.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          style={{
            border: isDragging ? "2px solid #3b82f6" : "2px dashed #475569",
            backgroundColor: isDragging ? "rgba(59, 130, 246, 0.1)" : "rgba(30, 41, 59, 0.5)",
            padding: "40px", borderRadius: "12px", textAlign: "center", cursor: "pointer", transition: "all 0.2s"
          }}
        >
          <input 
            type="file" accept="video/mp4,video/webm,video/quicktime" 
            style={{ display: "none" }} ref={fileInputRef} 
            onChange={(e) => { if (e.target.files[0]) setFile(e.target.files[0]); }} 
          />
          <div style={{ fontSize: "2.5rem", marginBottom: "10px" }}>
            {file ? "🎬" : "📥"}
          </div>
          <h4 style={{ margin: "0 0 5px 0", color: file ? "#3b82f6" : "#cbd5e1" }}>
            {file ? file.name : "Haz clic o arrastra tu video aquí"}
          </h4>
          <p style={{ color: "#64748b", fontSize: "0.85rem", margin: 0 }}>
            {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : `Formatos: MP4, MOV, WEBM (Max 50MB)`}
          </p>
        </div>
      )}
    </div>
  );
}