export default function InputTexto({ value, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px", width: "100%" }}>
      <textarea
        className="input-field"
        rows="6"
        placeholder="Pega el artículo, noticia, mensaje de WhatsApp o fragmento que deseas verificar aquí..."
        value={value}
        onChange={onChange}
        style={{ 
          resize: "vertical", 
          minHeight: "140px", 
          padding: "16px", 
          borderRadius: "10px",
          backgroundColor: "rgba(30, 41, 59, 0.5)",
          border: "1px solid #334155",
          color: "white",
          width: "100%",
          boxSizing: "border-box"
        }}
      />
      <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.8rem", padding: "0 4px" }}>
        <span>Asegúrate de incluir suficiente contexto para un mejor análisis.</span>
        <span style={{ color: value.length > 500 ? "#3b82f6" : "#64748b" }}>
          {value.length} caracteres
        </span>
      </div>
    </div>
  );
}