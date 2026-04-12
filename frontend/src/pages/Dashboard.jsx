import { useState, useEffect } from "react";
import "./Dashboard.css";
import { useUser, SignOutButton } from "@clerk/clerk-react";
import { PieChart, Pie, Cell, Tooltip } from "recharts";

export default function Dashboard() {

const { user } = useUser();

const [type,setType]=useState("texto");
const [filter,setFilter]=useState("all");

const [text,setText]=useState("");
const [url,setUrl]=useState("");
const [image,setImage]=useState(null);
const [video,setVideo]=useState(null);

const [preview,setPreview]=useState(null);
const [history,setHistory]=useState([]);
const [loading,setLoading]=useState(false);
const [progress,setProgress]=useState(0);
const [result,setResult]=useState(null);

// cargar historial
useEffect(()=>{
const data = JSON.parse(localStorage.getItem("history")) || [];
setHistory(data);
},[]);

// guardar historial
const saveHistory = (newHistory)=>{
localStorage.setItem("history", JSON.stringify(newHistory));
setHistory(newHistory);
};

// preview
const handleFile = (file)=>{
if(!file) return;
setPreview(URL.createObjectURL(file));
};

// analizar
const handleAnalyze = ()=>{

setLoading(true);
setProgress(0);
setResult(null);

let interval = setInterval(()=>{
setProgress(prev=>{
if(prev>=100){
clearInterval(interval);

const isFake = Math.random() > 0.5;

const res = {
type,
result: isFake ? "Fake ❌" : "Real 🟢",
confidence: Math.floor(Math.random()*40)+60,
date: new Date().toLocaleString()
};

setResult(res);
saveHistory([res,...history]);
setLoading(false);

return 100;
}
return prev+10;
});
},120);

};

// 📊 DATA PARA GRÁFICO
const realCount = history.filter(h=>h.result.includes("Real")).length;
const fakeCount = history.filter(h=>h.result.includes("Fake")).length;

const chartData = [
{ name: "Real", value: realCount },
{ name: "Fake", value: fakeCount }
];

// 🔎 FILTRO
const filteredHistory = history.filter(item=>{
if(filter==="real") return item.result.includes("Real");
if(filter==="fake") return item.result.includes("Fake");
return true;
});

return(

<div className="dashboard">

{/* NAVBAR */}
<div className="topbar">

<h2>FakeNewsAI</h2>

<div className="user-section">
<div>
<span className="name">{user?.fullName}</span>
<span className="email">{user?.primaryEmailAddress?.emailAddress}</span>
</div>

<span className="status">🟢 Activo</span>

<SignOutButton>
<button className="logout">Cerrar sesión</button>
</SignOutButton>
</div>

</div>

<div className="main">

{/* HISTORIAL */}
<div className="history">

<h3>Historial</h3>

{/* FILTROS */}
<div className="filters">
<button onClick={()=>setFilter("all")}>Todos</button>
<button onClick={()=>setFilter("real")}>Reales</button>
<button onClick={()=>setFilter("fake")}>Fake</button>
</div>

{filteredHistory.length===0 && <p>No hay datos</p>}

{filteredHistory.map((item,i)=>(
<div key={i} className="history-item">
<strong>{item.type}</strong>
<p>{item.result}</p>
<small>{item.date}</small>
</div>
))}

</div>

{/* CENTRO */}
<div className="center">

<div className="hero">
<h1>Centro de verificación</h1>
<p>Analiza contenido digital en segundos</p>
</div>

{/* 📊 STATS */}
<div className="stats">

<div className="card">
<h4>Total</h4>
<p>{history.length}</p>
</div>

<div className="card">
<h4>Reales</h4>
<p>{realCount}</p>
</div>

<div className="card">
<h4>Fake</h4>
<p>{fakeCount}</p>
</div>

</div>

{/* 📊 GRAFICO */}
<div className="chart">
<PieChart width={200} height={200}>
<Pie
data={chartData}
cx="50%"
cy="50%"
outerRadius={70}
dataKey="value"
>
<Cell fill="#22c55e" />
<Cell fill="#ef4444" />
</Pie>
<Tooltip />
</PieChart>
</div>

{/* PANEL */}
<div className="analysis-panel">

<div className="tabs">
<button className={type==="texto"?"active":""} onClick={()=>setType("texto")}>Texto</button>
<button className={type==="url"?"active":""} onClick={()=>setType("url")}>URL</button>
<button className={type==="imagen"?"active":""} onClick={()=>setType("imagen")}>Imagen</button>
<button className={type==="video"?"active":""} onClick={()=>setType("video")}>Video</button>
</div>

{type==="texto" && (
<textarea value={text} onChange={(e)=>setText(e.target.value)} />
)}

{type==="url" && (
<input value={url} onChange={(e)=>setUrl(e.target.value)} />
)}

{type==="imagen" && (
<>
<input type="file" onChange={(e)=>{
setImage(e.target.files[0]);
handleFile(e.target.files[0]);
}} />
{preview && <img src={preview} className="preview"/>}
</>
)}

{type==="video" && (
<>
<input type="file" onChange={(e)=>{
setVideo(e.target.files[0]);
handleFile(e.target.files[0]);
}} />
{preview && <video src={preview} controls className="preview"/>}
</>
)}

<button className="verify-btn" onClick={handleAnalyze}>
Analizar
</button>

{loading && (
<div className="progress-bar" style={{width:`${progress}%`}}></div>
)}

{result && (
<div className={`result ${result.result.includes("Fake")?"fake":"real"}`}>
<h3>{result.result}</h3>
<p>{result.confidence}%</p>
</div>
)}

</div>

</div>

</div>

</div>

);
}