import { useState, useEffect } from "react";
import { useUser, SignOutButton, UserButton } from "@clerk/clerk-react";
import Sidebar from "../components/Sidebar.jsx";
import DashboardCenter from "../pages/DashboardCenter.jsx";
import "./DashboardLayout.css";

export default function DashboardLayout() {
  const { user } = useUser();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const data = JSON.parse(localStorage.getItem("history")) || [];
    setHistory(data);
  }, []);

  const saveHistory = (newHistory) => {
    localStorage.setItem("history", JSON.stringify(newHistory));
    setHistory(newHistory);
  };

  return (
    <div className="dashboard-wrapper">
      {/* TOPBAR MINIMALISTA */}
      <header className="topbar">
        <h2 className="logo" style={{fontSize: "1.2rem"}}>FakeNews<span>AI</span></h2>
        
        <div className="user-section">
          <div className="user-info">
            <span className="user-name">{user?.fullName || "Analista"}</span>
            <span className="user-email">{user?.primaryEmailAddress?.emailAddress}</span>
          </div>
          {/* Avatar de Google */}
          <UserButton afterSignOutUrl="/" />
          
          <SignOutButton>
            <button className="logout-btn">Salir</button>
          </SignOutButton>
        </div>
      </header>

      <div className="dashboard-main">
        <Sidebar history={history} />
        <DashboardCenter history={history} setHistory={saveHistory} />
      </div>
    </div>
  );
}