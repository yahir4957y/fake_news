import { useUser } from "@clerk/clerk-react";

export default function AdminRoute({ children }) {
  const { isLoaded, isSignedIn, user } = useUser();

  if (!isLoaded) {
    return (
      <div style={styles.center}>
        <p style={styles.msg}>Verificando acceso...</p>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div style={styles.center}>
        <p style={styles.msg}>Debes iniciar sesión.</p>
      </div>
    );
  }

  const role = user?.publicMetadata?.role;

  if (role !== "admin") {
    return (
      <div style={styles.center}>
        <div style={styles.box}>
          <p style={styles.icon}>🚫</p>
          <p style={styles.title}>Acceso restringido</p>
          <p style={styles.sub}>No tienes permisos para ver esta sección.</p>
        </div>
      </div>
    );
  }

  return children;
}

const styles = {
  center: { display:"flex", alignItems:"center", justifyContent:"center", minHeight:"100vh", background:"#020617" },
  box:    { textAlign:"center", padding:"40px 32px", background:"#0f172a", border:"1px solid #1e293b", borderRadius:12 },
  icon:   { fontSize:40, marginBottom:12 },
  title:  { fontSize:18, fontWeight:600, color:"#f1f5f9", marginBottom:8 },
  sub:    { fontSize:14, color:"#64748b" },
  msg:    { color:"#64748b", fontSize:14 },
};