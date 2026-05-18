import { useUser, useAuth } from '@clerk/clerk-react';
import { useEffect, useState } from 'react';
import '../styles/TokenDashboard.css';

const API = 'http://localhost:8000';

const TokenDashboard = ({ onBack }) => {
  const { user } = useUser();
  const { getToken } = useAuth();

  const [myStats, setMyStats] = useState(null);
  const [globalStats, setGlobalStats] = useState(null);
  const [allUsersStats, setAllUsersStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;

    const fetchStats = async () => {
      try {
        const token = await getToken();
        const headers = { Authorization: `Bearer ${token}` };

        const [myRes, globalRes, allUsersRes] = await Promise.all([
          fetch(`${API}/api/tokens/my-stats`, { headers }),
          fetch(`${API}/api/tokens/global-stats`, { headers }),
          fetch(`${API}/api/tokens/all-users-stats`, { headers }),
        ]);

        if (myRes.ok) setMyStats(await myRes.json());
        if (globalRes.ok) setGlobalStats(await globalRes.json());
        if (allUsersRes.ok) setAllUsersStats(await allUsersRes.json());
      } catch (error) {
        console.error('Error al cargar estadísticas de tokens:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user, getToken]);

  if (loading) {
    return (
      <div className="token-page">
        <div className="token-container">
          <div className="token-loading">Cargando estadísticas...</div>
        </div>
      </div>
    );
  }

  const fmt = (n) => (n ?? 0).toLocaleString();
  const fmtDate = (d) => d ? new Date(d).toLocaleDateString('es-ES') : 'N/A';

  return (
    <div className="token-page">
    <div className="token-container">
      <div className="token-header">
        <button className="token-back-btn" onClick={onBack}>
          ← Volver al Dashboard
        </button>
        <div className="token-title-group">
          <p className="token-page-tag">Panel de Tokens</p>
          <h1>📊 Gestión del consumo de Gemini</h1>
        </div>
      </div>

      <section className="token-section token-main-section">
        <h2>Mi Consumo</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <p className="stat-label">Tokens Usados</p>
            <p className="stat-value">{fmt(myStats?.data?.tokens_used)}</p>
          </div>
          <div className="stat-card">
            <p className="stat-label">Análisis Realizados</p>
            <p className="stat-value">{fmt(myStats?.data?.requests_count)}</p>
          </div>
          <div className="stat-card">
            <p className="stat-label">Email</p>
            <p className="stat-value" style={{ fontSize: '1rem' }}>
              {myStats?.data?.email || user?.primaryEmailAddress?.emailAddress || '—'}
            </p>
          </div>
          <div className="stat-card">
            <p className="stat-label">Último Uso</p>
            <p className="stat-value">{fmtDate(myStats?.data?.last_request)}</p>
          </div>
        </div>
      </section>

      {/* Resumen global */}
      <section className="token-section">
        <h2>🌍 Resumen Global del Sistema</h2>
        <div className="stats-grid">
          <div className="stat-card global">
            <p className="stat-label">Total Tokens en el Sistema</p>
            <p className="stat-value">{fmt(globalStats?.data?.total_tokens_used)}</p>
          </div>
          <div className="stat-card global">
            <p className="stat-label">Total de Análisis</p>
            <p className="stat-value">{fmt(globalStats?.data?.total_requests)}</p>
          </div>
        </div>
      </section>

      {/* Tabla de usuarios */}
      <section className="token-section">
        <h2>👥 Consumo por Usuario</h2>
        {allUsersStats?.data?.length > 0 ? (
          <div className="table-container table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Tokens Usados</th>
                  <th>Análisis</th>
                  <th>Último Uso</th>
                </tr>
              </thead>
              <tbody>
                {allUsersStats.data.map((u, idx) => (
                  <tr key={idx}>
                    <td>{u.email || '—'}</td>
                    <td>{fmt(u.tokens_used)}</td>
                    <td>{u.requests_count}</td>
                    <td>{fmtDate(u.last_request)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: '#64748b' }}>
            Aún no hay datos. Realiza un análisis para que aparezca aquí.
          </p>
        )}
      </section>
    </div>
    </div>
  );
};

export default TokenDashboard;
