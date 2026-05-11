export default function InputUrl({ value, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px", width: "100%" }}>
      <div style={{ position: "relative", display: "flex", alignItems: "center", width: "100%" }}>
        <span style={{ 
          position: "absolute", 
          left: "16px", 
          top: "50%", 
          transform: "translateY(-50%)", 
          fontSize: "1.2rem",
          pointerEvents: "none",
          opacity: 0.7,
          display: "flex", /* 🔥 Asegura que el ícono no tenga márgenes raros */
          alignItems: "center"
        }}>
          🔗
        </span>
        <input
          type="text"
          className="input-field"
          placeholder="Ej: https://x.com/noticia-sospechosa o https://facebook.com/..."
          value={value}
          onChange={onChange}
          style={{ 
            padding: "0 16px 0 48px", /* 🔥 Forzamos padding 0 arriba y abajo, 48px a la izquierda */
            width: "100%", 
            height: "55px", 
            lineHeight: "55px", /* 🔥 TRUCO: Iguala al height para centrar el texto verticalmente sí o sí */
            borderRadius: "10px",
            backgroundColor: "rgba(30, 41, 59, 0.5)",
            border: "1px solid #334155",
            color: "white",
            boxSizing: "border-box"
          }}
        />
      </div>
      <p style={{ color: "#64748b", fontSize: "0.85rem", margin: 0, padding: "0 4px" }}>
        Ingresa enlaces de portales de noticias, Facebook, X (Twitter) o TikTok.
      </p>
    </div>
  );
}