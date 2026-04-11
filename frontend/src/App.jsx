import { useState, useEffect } from "react";
import "./App.css";

// Contenido más profesional para el sistema
const slides = [
  {
    title: "Detección Precisa",
    text: "Sistema inteligente de verificación de contenido digital mediante redes neuronales."
  },
  {
    title: "Análisis Multimedia",
    text: "Analiza noticias, imágenes y videos para identificar patrones de desinformación."
  },
  {
    title: "Protección en Tiempo Real",
    text: "Herramientas avanzadas para combatir la propagación de Fake News en segundos."
  }
];

function App() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % slides.length);
    }, 4000); // 4 segundos es ideal para leer frases cortas

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      
      {/* Navbar */}
      <nav className="navbar">
        <h2 className="logo">FakeNews<span>AI</span></h2>
        <div className="nav-buttons">
          <button className="btn-outline">Iniciar sesión</button>
          <button className="btn-primary">Registrarse</button>
        </div>
      </nav>

      {/* Hero */}
      <section className="hero">
        <h1>Detecta la verdad tras la <span>desinformación</span></h1>

        {/* Carrusel con animación */}
        <div className="carousel">
          <div key={index} className="slide-content">
            <h3 style={{ color: "var(--primary)", marginBottom: "10px" }}>
                {slides[index].title}
            </h3>
            <p>{slides[index].text}</p>
          </div>
        </div>

        <button className="btn-start">Comenzar Análisis</button>
      </section>

    </div>
  );
}

export default App;