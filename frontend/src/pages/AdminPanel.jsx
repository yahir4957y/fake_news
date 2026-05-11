// frontend/src/pages/AdminPanel.jsx
import { useState, useEffect } from "react";
import { useAuth, useClerk } from "@clerk/clerk-react";
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from "recharts";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TIPO_COLORS = {
  texto: "#378ADD",
  imagen: "#1D9E75",
  url: "#EF9F27",
  otro: "#64748b",
};

const STATUS_META = {
  activa: { label: "Activa", color: "#4ade80", bg: "rgba(34,197,94,0.1)", border: "#166534" },
  sin_configurar: { label: "Sin configurar", color: "#fbbf24", bg: "rgba(245,158,11,0.1)", border: "#92400e" },
  no_implementada: { label: "Futura", color: "#93c5fd", bg: "rgba(59,130,246,0.1)", border: "#1d4ed8" },
  error: { label: "Error", color: "#f87171", bg: "rgba(239,68,68,0.1)", border: "#7f1d1d" },
};

function generarHorasVacias() {
  const ahora = new Date();
  return Array.from({ length: 12 }, (_, i) => {
    const h = new Date(ahora);
    h.setHours(ahora.getHours() - (11 - i), 0, 0, 0);
    return { hora: `${h.getHours()}h`, solicitudes: 0 };
  });
}

export default function AdminPanel() {
  const { getToken } = useAuth();
  const { signOut } = useClerk();
  const [activeSection, setActiveSection] = useState("metricas");
  const [metricas, setMetricas] = useState(null);
  const [apiCatalog, setApiCatalog] = useState([]);
  const [apiMessages, setApiMessages] = useState({});
  const [loadingMetricas, setLoadingMetricas] = useState(true);
  const [loadingApis, setLoadingApis] = useState(true);
  const [testingApis, setTestingApis] = useState({});
  const [toast, setToast] = useState(null);

  useEffect(() => {
    loadData();
    loadApis();
  }, []);

  async function fetchAuth(path, options = {}) {
    const token = await getToken();
    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Error del servidor");
    }

    return res.json();
  }

  async function loadData() {
    setLoadingMetricas(true);
    try {
      const data = await fetchAuth("/api/admin/metricas");
      setMetricas(data);
    } catch (err) {
      showToast("Error al cargar metricas: " + err.message, "error");
    } finally {
      setLoadingMetricas(false);
    }
  }

  async function loadApis() {
    setLoadingApis(true);
    try {
      const data = await fetchAuth("/api/admin/apis");
      setApiCatalog(data.apis || []);
    } catch (err) {
      showToast("Error al cargar APIs: " + err.message, "error");
    } finally {
      setLoadingApis(false);
    }
  }

  async function refreshCurrent() {
    if (activeSection === "apis") {
      await loadApis();
      return;
    }
    await loadData();
  }

  async function testApi(apiId) {
    setTestingApis((current) => ({ ...current, [apiId]: true }));
    setApiMessages((current) => ({ ...current, [apiId]: null }));

    try {
      const data = await fetchAuth(`/api/admin/apis/${apiId}/test`, { method: "POST" });
      setApiCatalog((current) =>
        current.map((api) => api.id === apiId ? { ...api, estado: data.estado } : api)
      );
      setApiMessages((current) => ({ ...current, [apiId]: data.mensaje }));
      showToast(data.mensaje, data.success ? "success" : "error");
    } catch (err) {
      setApiMessages((current) => ({ ...current, [apiId]: err.message }));
      showToast("Error al probar API: " + err.message, "error");
    } finally {
      setTestingApis((current) => ({ ...current, [apiId]: false }));
    }
  }

  function showToast(msg, type = "success") {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 2800);
  }

  const contenidosPorTipo = metricas?.contenidos_por_tipo || [];
  const solicitudesPorHora = (metricas?.solicitudes_por_hora?.length > 0)
    ? metricas.solicitudes_por_hora
    : generarHorasVacias();

  const s = {
    wrap: { fontFamily: "sans-serif", color: "#e2e8f0", minHeight: "100vh", background: "#020617" },
    nav: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 24px", borderBottom: "1px solid #1e293b", background: "#0f172a" },
    logo: { fontSize: 16, fontWeight: 600, color: "#fff" },
    badge: { fontSize: 11, padding: "3px 8px", background: "#1e3a5f", color: "#60a5fa", borderRadius: 6, marginLeft: 8 },
    navBtns: { display: "flex", gap: 8, alignItems: "center" },
    btnRef: { padding: "6px 16px", borderRadius: 6, border: "1px solid #334155", background: "transparent", color: "#e2e8f0", fontSize: 13, cursor: "pointer" },
    btnOut: { padding: "6px 16px", borderRadius: 6, border: "1px solid #450a0a", background: "transparent", color: "#f87171", fontSize: 13, cursor: "pointer" },
    content: { padding: 24 },
    tabs: { display: "flex", gap: 8, marginBottom: 20, borderBottom: "1px solid #1e293b" },
    tab: (active) => ({
      background: "transparent",
      border: "none",
      borderBottom: `2px solid ${active ? "#3b82f6" : "transparent"}`,
      color: active ? "#60a5fa" : "#64748b",
      cursor: "pointer",
      fontSize: 14,
      fontWeight: 600,
      padding: "0 4px 12px",
    }),
    grid2: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 12, marginBottom: 24 },
    metric: { background: "#0f172a", border: "1px solid #1e293b", borderRadius: 10, padding: "14px 16px" },
    mLbl: { fontSize: 12, color: "#64748b", marginBottom: 6 },
    mVal: { fontSize: 32, fontWeight: 700, color: "#f1f5f9" },
    mSub: { fontSize: 11, color: "#475569", marginTop: 4 },
    twoCol: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 16, marginBottom: 16 },
    card: { background: "#0f172a", border: "1px solid #1e293b", borderRadius: 10, padding: "16px 18px" },
    cardFull: { background: "#0f172a", border: "1px solid #1e293b", borderRadius: 10, padding: "16px 18px", marginBottom: 16 },
    cTitle: { fontSize: 11, fontWeight: 600, color: "#475569", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 14 },
    empty: { color: "#475569", fontSize: 13, marginTop: 16 },
    apiGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 16 },
    apiCard: { background: "#0f172a", border: "1px solid #1e293b", borderRadius: 10, padding: 18, display: "flex", flexDirection: "column", gap: 14 },
    apiTop: { display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 },
    apiName: { fontSize: 17, fontWeight: 700, color: "#f8fafc", marginBottom: 4 },
    apiProvider: { fontSize: 12, color: "#64748b" },
    apiUse: { color: "#cbd5e1", fontSize: 13, lineHeight: 1.5 },
    envBox: { background: "#020617", border: "1px solid #1e293b", borderRadius: 8, padding: "10px 12px", color: "#93c5fd", fontSize: 12, fontFamily: "monospace" },
    testBtn: (disabled) => ({
      padding: "8px 14px",
      borderRadius: 7,
      border: "1px solid #334155",
      background: disabled ? "#1e293b" : "#020617",
      color: disabled ? "#64748b" : "#e2e8f0",
      cursor: disabled ? "not-allowed" : "pointer",
      fontSize: 13,
      fontWeight: 600,
      alignSelf: "flex-start",
    }),
    message: { color: "#94a3b8", fontSize: 12, lineHeight: 1.5 },
    toast: (t) => ({
      position: "fixed",
      bottom: 20,
      right: 20,
      background: t === "error" ? "#450a0a" : "#14532d",
      color: t === "error" ? "#f87171" : "#4ade80",
      border: "1px solid " + (t === "error" ? "#7f1d1d" : "#166634"),
      borderRadius: 8,
      padding: "10px 16px",
      fontSize: 13,
      zIndex: 200,
      maxWidth: 420,
    }),
  };

  const TT = ({ active, payload, label, unit = "" }) =>
    !active || !payload?.length ? null : (
      <div style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 8, padding: "8px 12px" }}>
        <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 4 }}>{label}</p>
        <p style={{ fontSize: 14, fontWeight: 600, color: "#f1f5f9" }}>{payload[0].value} {unit}</p>
      </div>
    );

  function StatusBadge({ estado }) {
    const meta = STATUS_META[estado] || STATUS_META.error;
    return (
      <span style={{
        background: meta.bg,
        border: `1px solid ${meta.border}`,
        color: meta.color,
        borderRadius: 999,
        padding: "4px 10px",
        fontSize: 11,
        fontWeight: 700,
        whiteSpace: "nowrap",
      }}>
        {meta.label}
      </span>
    );
  }

  function renderMetricas() {
    if (loadingMetricas) {
      return (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}>
          <p style={{ color: "#64748b" }}>Cargando datos...</p>
        </div>
      );
    }

    return (
      <>
        <div style={s.grid2}>
          <div style={s.metric}>
            <div style={s.mLbl}>Usuarios registrados</div>
            <div style={s.mVal}>{metricas?.total_usuarios ?? 0}</div>
            <div style={s.mSub}>en Supabase</div>
          </div>
          <div style={s.metric}>
            <div style={s.mLbl}>Analisis totales</div>
            <div style={s.mVal}>{metricas?.total_contenidos ?? 0}</div>
            <div style={s.mSub}>contenidos enviados</div>
          </div>
        </div>

        <div style={s.twoCol}>
          <div style={s.card}>
            <div style={s.cTitle}>Contenidos por tipo</div>
            {contenidosPorTipo.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={contenidosPorTipo} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                  <XAxis dataKey="tipo" tick={{ fill: "#475569", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<TT unit="contenidos" />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                  <Bar dataKey="cantidad" radius={[4, 4, 0, 0]}>
                    {contenidosPorTipo.map((c, i) => (
                      <Cell key={i} fill={TIPO_COLORS[c.tipo] || "#64748b"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : <p style={s.empty}>Sin datos aun.</p>}
          </div>

          <div style={s.card}>
            <div style={s.cTitle}>Desglose por tipo</div>
            {contenidosPorTipo.length > 0 ? (
              <div style={{ marginTop: 8 }}>
                {contenidosPorTipo.map((c, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 0", borderBottom: i < contenidosPorTipo.length - 1 ? "1px solid #1e293b" : "none" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div style={{ width: 10, height: 10, borderRadius: "50%", background: TIPO_COLORS[c.tipo] || "#64748b" }} />
                      <span style={{ fontSize: 14, color: "#cbd5e1", textTransform: "capitalize" }}>{c.tipo}</span>
                    </div>
                    <span style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9" }}>{c.cantidad}</span>
                  </div>
                ))}
              </div>
            ) : <p style={s.empty}>Sin datos aun.</p>}
          </div>
        </div>

        <div style={s.cardFull}>
          <div style={s.cTitle}>Solicitudes por hora (ultimas 12h)</div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={solicitudesPorHora} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <XAxis dataKey="hora" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip content={<TT unit="solicitudes" />} />
              <Line type="monotone" dataKey="solicitudes" stroke="#1D9E75" strokeWidth={2} dot={{ fill: "#1D9E75", r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </>
    );
  }

  function renderApis() {
    if (loadingApis) {
      return (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}>
          <p style={{ color: "#64748b" }}>Cargando APIs...</p>
        </div>
      );
    }

    return (
      <>
        <div style={{ marginBottom: 18 }}>
          <h1 style={{ fontSize: 24, marginBottom: 6, color: "#f8fafc" }}>Gestion de APIs</h1>
          <p style={{ color: "#94a3b8", fontSize: 14 }}>
            Estado de proveedores externos configurados desde el backend. Las claves privadas no se muestran en pantalla.
          </p>
        </div>

        <div style={s.apiGrid}>
          {apiCatalog.map((api) => (
            <div key={api.id} style={s.apiCard}>
              <div style={s.apiTop}>
                <div>
                  <div style={s.apiName}>{api.nombre}</div>
                  <div style={s.apiProvider}>{api.proveedor}</div>
                </div>
                <StatusBadge estado={api.estado} />
              </div>

              <div style={s.apiUse}>{api.uso}</div>

              <div>
                <div style={{ ...s.cTitle, marginBottom: 8 }}>Variable requerida</div>
                <div style={s.envBox}>{api.variable_env}</div>
              </div>

              <button
                onClick={() => testApi(api.id)}
                disabled={Boolean(testingApis[api.id])}
                style={s.testBtn(Boolean(testingApis[api.id]))}
              >
                {testingApis[api.id] ? "Probando..." : "Probar conexion"}
              </button>

              {apiMessages[api.id] && (
                <div style={s.message}>{apiMessages[api.id]}</div>
              )}
            </div>
          ))}
        </div>
      </>
    );
  }

  return (
    <div style={s.wrap}>
      <div style={s.nav}>
        <div style={s.logo}>
          <span style={{ color: "#3b82f6" }}>FakeNews</span>AI
          <span style={s.badge}>Admin</span>
        </div>
        <div style={s.navBtns}>
          <button onClick={refreshCurrent} style={s.btnRef}>Actualizar</button>
          <button onClick={() => signOut()} style={s.btnOut}>Cerrar sesion</button>
        </div>
      </div>

      <div style={s.content}>
        <div style={s.tabs}>
          <button style={s.tab(activeSection === "metricas")} onClick={() => setActiveSection("metricas")}>
            Metricas
          </button>
          <button style={s.tab(activeSection === "apis")} onClick={() => setActiveSection("apis")}>
            Gestion de APIs
          </button>
        </div>

        {activeSection === "metricas" ? renderMetricas() : renderApis()}
      </div>

      {toast && <div style={s.toast(toast.type)}>{toast.msg}</div>}
    </div>
  );
}
