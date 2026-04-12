import { useState, useEffect } from "react";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton
} from "@clerk/clerk-react";
import "./App.css";
import Dashboard from "./pages/Dashboard";

// Carrusel
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
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* 🔐 SI ESTA LOGUEADO → DASHBOARD */}
      <SignedIn>
        <Dashboard />
      </SignedIn>

      {/* 🚪 SI NO ESTA LOGUEADO → LANDING */}
      <SignedOut>
        <div className="container">

          {/* NAVBAR */}
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

          {/* HERO */}
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

            <SignInButton mode="modal">
              <button className="btn-start">
                Comenzar Análisis
              </button>
            </SignInButton>
          </section>
        </div>
      </SignedOut>
    </>
  );
}

export default App;