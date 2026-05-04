import { useRef, useState } from "react";

export default function SubidaImagen({ file, setFile }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  // 1. Evita que el navegador abra la imagen al arrastrarla encima
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  // 2. Captura el archivo cuando lo sueltas
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      // Validamos que sea una imagen
      if (droppedFile.type.startsWith("image/")) {
        setFile(droppedFile);
      } else {
        alert("Por favor, sube solo archivos de imagen.");
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`upload-zone ${file ? 'active' : ''} ${isDragging ? 'dragging' : ''}`}
      onClick={() => fileInputRef.current.click()}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      style={{
        border: isDragging ? "2px solid #3b82f6" : "2px dashed #475569",
        backgroundColor: isDragging ? "rgba(59, 130, 246, 0.1)" : "transparent",
        transition: "all 0.2s ease",
        padding: "40px",
        borderRadius: "12px",
        textAlign: "center",
        cursor: "pointer"
      }}
    >
      <input 
        type="file" 
        accept="image/*" 
        style={{ display: "none" }} 
        ref={fileInputRef} 
        onChange={handleFileChange} 
      />
      <div style={{ fontSize: "2.5rem", marginBottom: "10px" }}>
        {file ? "🖼️" : isDragging ? "📩" : "📸"}
      </div>
      <h4 style={{ margin: "0 0 5px 0", color: file ? "#3b82f6" : "#cbd5e1" }}>
        {file ? file.name : isDragging ? "¡Suéltala ahora!" : "Haz clic o arrastra tu imagen aquí"}
      </h4>
      <p style={{ color: "#64748b", fontSize: "0.85rem", margin: 0 }}>
        {file 
          ? `${(file.size / 1024 / 1024).toFixed(2)} MB` 
          : `Formatos soportados: JPG, PNG, WEBP`}
      </p>
    </div>
  );
}