// src/pages/Landing.jsx
import { useState, useEffect } from "react";
import { SignInButton, SignUpButton } from "@clerk/clerk-react";

// El contenido del Carrusel
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

export default function Landing() {
  const [index, setIndex] = useState(0);

  // Animación automática del carrusel
  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % slides.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      {/* NAVBAR PÚBLICO */}
      <nav className="navbar">
        <h2 className="logo">FakeNews<span>AI</span></h2>
        
        <div className="nav-buttons">
          <SignInButton mode="modal">
            <button className="btn-outline">Iniciar sesión</button>
          </SignInButton>

          <SignUpButton mode="modal">
            <button className="btn-primary">Registrarse</button>
          </SignUpButton>
        </div>
      </nav>

      {/* SECCIÓN PRINCIPAL (HERO) */}
      <section className="hero">
        <h1>
          Detecta la verdad tras la <span>desinformación</span>
        </h1>

        {/* Carrusel */}
        <div className="carousel">
          <div key={index} className="slide-content">
            <h3 style={{ color: "var(--primary)", marginBottom: "10px" }}>
              {slides[index].title}
            </h3>
            <p>{slides[index].text}</p>
          </div>
        </div>

        {/* Botón de llamada a la acción */}
        <SignInButton mode="modal">
          <button className="btn-start">
            Comenzar Análisis
          </button>
        </SignInButton>
      </section>
    </div>
  );
}