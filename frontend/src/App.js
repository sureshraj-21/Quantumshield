import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2'; 
import { jsPDF } from "jspdf"; 
import html2canvas from 'html2canvas';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, 
  BarElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler);

// ===============================
// 🚀 PRODUCTION API CONFIG
// ===============================
const BASE_URL = "https://quantumshield-3b12.onrender.com";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [data, setData] = useState(null);
  const [selectedStock, setSelectedStock] = useState("HDFCBANK.NS");
  const [loading, setLoading] = useState(false);
  const [authData, setAuthData] = useState({ username: '', password: '', email: '' });
  const [isVoiceMuted, setIsVoiceMuted] = useState(false);

  const [wallet, setWallet] = useState(100000); 
  const [holdings, setHoldings] = useState({}); 
  const [livePrice, setLivePrice] = useState(0); 
  const [priceHistory, setPriceHistory] = useState([]); 
  const [investment, setInvestment] = useState(10000);
  const [mcResult, setMcResult] = useState(null);

  const [isGhostHedgeActive, setIsGhostHedgeActive] = useState(true);
  const [isAutoExecutionActive, setIsAutoExecutionActive] = useState(true);
  const [isWhatsappEnabled, setIsWhatsappEnabled] = useState(true); 
  const [isAlertEnabled, setIsAlertEnabled] = useState(true); 
  const [sensitivity, setSensitivity] = useState(85);

  const MY_PHONE = "+919962126306";

  const sendSilentAlert = async (message) => {
    if (!isAlertEnabled) return;
    try {
        await axios.post(`${BASE_URL}/api/send-notification`, {
            msg: message,
            phone: MY_PHONE
        });
    } catch (error) {
        console.error("Notification failed", error);
    }
  };

  const stockList = [
    { name: "HDFC Bank (₹816 Proof)", symbol: "HDFCBANK.NS" },
    { name: "SBI", symbol: "SBIN.NS" },
    { name: "ICICI Bank", symbol: "ICICIBANK.NS" },
    { name: "Reliance Industries", symbol: "RELIANCE.NS" },
    { name: "TCS", symbol: "TCS.NS" },
    { name: "Infosys", symbol: "INFY.NS" },
    { name: "Adani Enterprises", symbol: "ADANIENT.NS" },
    { name: "ITC", symbol: "ITC.NS" }
  ];

  const fetchData = (symbol) => {
    setLoading(true);
    axios.get(`${BASE_URL}/api/analyze?tickers=${symbol}`)
      .then(res => {
        setData(Array.isArray(res.data) ? res.data[0] : res.data);
        setLoading(false);
      }).catch(() => setLoading(false));
  };

  useEffect(() => { if (isLoggedIn) fetchData(selectedStock); }, [selectedStock, isLoggedIn]);

  useEffect(() => {
    if (isLoggedIn && data) {
      setLivePrice(data.current_price);
      setPriceHistory([data.current_price]);
      const interval = setInterval(() => {
        setLivePrice(prevPrice => {
          const fluctuation = (Math.random() - 0.5) * 4.0; 
          const newPrice = prevPrice + fluctuation;
          if (isAutoExecutionActive && holdings[data.symbol]?.qty > 0) {
              const holding = holdings[data.symbol];
              const targetPrice = holding.avgPrice + 4.5;   
              const stopLossPrice = holding.avgPrice - 10.0; 
              if (newPrice >= targetPrice || newPrice <= stopLossPrice) {
                executeTrade("SELL", true);
                sendSilentAlert(`🚨 AUTO-SELL: ${data.symbol} at ₹${newPrice.toFixed(2)}`);
              }
          }
          setPriceHistory(history => [...history, newPrice].slice(-20));
          return newPrice;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [data, isLoggedIn, isAutoExecutionActive, holdings]);

  const executeTrade = (action, isAuto = false) => {
    if (!data) return;
    const price = livePrice;
    const symbol = data.symbol;
    if (action === "BUY" && wallet >= price) {
        setWallet(prev => prev - price);
        setHoldings(prev => {
          const current = prev[symbol] || { qty: 0, avgPrice: 0 };
          const newQty = current.qty + 1;
          const newAvg = ((current.avgPrice * current.qty) + price) / newQty;
          return { ...prev, [symbol]: { qty: newQty, avgPrice: newAvg } };
        });
        sendSilentAlert(`🛡️ MANUAL BUY: ${symbol} @ ₹${price.toFixed(2)}`);
    } else if (action === "SELL" && holdings[symbol]?.qty > 0) {
        const saleAmount = price * holdings[symbol].qty;
        setWallet(prev => prev + saleAmount);
        setHoldings(prev => {
          const updated = { ...prev };
          delete updated[symbol];
          return updated;
        });
        if (!isAuto) sendSilentAlert(`🚨 MANUAL SELL: ${symbol} @ ₹${price.toFixed(2)}`);
    }
  };

  const runMonteCarlo = () => {
    if (!data) return;
    setLoading(true);
    setTimeout(() => {
      const bsiVal = parseFloat(data.bsi_score); 
      const volVal = parseFloat(data.volatility);
      setMcResult({
        profit: (investment * (bsiVal / 100) * 1.3).toFixed(2),
        loss: (investment * (volVal / 100) * 0.6).toFixed(2),
        verdict: bsiVal >= 50 ? "BUY" : "AVOID",
        color: bsiVal >= 50 ? "#10b981" : "#ef4444",
        ghostHedgeStatus: "ACTIVE"
      });
      setLoading(false);
    }, 1000);
  };

  const handleAuth = async () => {
    const endpoint = isRegisterMode ? 'signup' : 'login';
    try {
      const res = await axios.post(`${BASE_URL}/auth/${endpoint}`, authData);
      if (res.data) {
        setIsLoggedIn(true);
        sendSilentAlert(`🔐 ${endpoint.toUpperCase()}: ${authData.username}`);
      }
    } catch (err) {
      alert(isRegisterMode ? "Error! Username exists or server down." : "Invalid Credentials!");
    }
  };

  const downloadReport = () => {
    const input = document.getElementById('report-area');
    html2canvas(input).then((canvas) => {
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      pdf.addImage(imgData, 'PNG', 0, 0, 210, (canvas.height * 210) / canvas.width);
      pdf.save(`QuantShield_Report.pdf`);
    });
  };

  const speakStatus = () => {
    if (!data || isVoiceMuted) return;
    window.speechSynthesis.cancel();
    const msg = new SpeechSynthesisUtterance(`QuantShield report for ${data.symbol}. Score is ${data.bsi_score}. Recommendation: ${data.decision}.`);
    window.speechSynthesis.speak(msg);
  };

  // --- RENDERING LOGIC (Style remains exactly as you provided) ---
  const liveGraphData = {
    labels: priceHistory.map((_, i) => `${i}s`),
    datasets: [{ label: `Live Trend (₹)`, data: priceHistory, borderColor: '#00f2fe', backgroundColor: 'rgba(79, 172, 254, 0.1)', fill: true, tension: 0.4, pointRadius: 0 }]
  };

  const pieData = {
    labels: ['Equities', 'Hedge', 'Cash'],
    datasets: [{ data: [60, 25, 15], backgroundColor: ['#00f2fe', '#f87171', '#94a3b8'], borderWidth: 0 }]
  };

  if (!isLoggedIn) {
    return (
      <div style={{ 
        backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://i.ibb.co/XfXkY8C/rm373batch4-07.jpg')`, 
        backgroundSize: 'cover', backgroundPosition: 'center', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: "'Poppins', sans-serif" 
      }}>
        <div style={{ background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(15px)', padding: '50px', borderRadius: '30px', width: '950px', display: 'flex', gap: '40px', color: 'white', border: '1px solid rgba(255,255,255,0.2)' }}>
          <div style={{ flex: 1.2, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
             <h1 style={{ fontSize: '56px', fontWeight: '900', color: '#00f2fe', marginBottom: '10px' }}>QuantShield</h1>
             <p style={{ fontSize: '18px', opacity: 0.8 }}>Advanced AI-Driven Portfolio Optimization System.<br/><span style={{ color: '#10b981', fontWeight: 'bold' }}>🛡️ Ghost Hedge Active</span></p>
          </div>
          <div style={{ flex: 0.8, background: 'rgba(0, 0, 0, 0.4)', padding: '40px', borderRadius: '25px' }}>
            <h2 style={{ marginBottom: '25px' }}>{isRegisterMode ? "REGISTER" : "LOGIN"}</h2>
            <input type="text" placeholder="USERNAME" onChange={(e) => setAuthData({...authData, username: e.target.value})} style={{ width: '100%', padding: '14px', margin: '12px 0', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.3)', color: 'white', borderRadius: '12px' }} />
            {isRegisterMode && <input type="email" placeholder="EMAIL" onChange={(e) => setAuthData({...authData, email: e.target.value})} style={{ width: '100%', padding: '14px', margin: '12px 0', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.3)', color: 'white', borderRadius: '12px' }} />}
            <input type="password" placeholder="PASSWORD" onChange={(e) => setAuthData({...authData, password: e.target.value})} style={{ width: '100%', padding: '14px', margin: '12px 0', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.3)', color: 'white', borderRadius: '12px' }} />
            <button onClick={handleAuth} style={{ width: '100%', padding: '16px', marginTop: '15px', background: 'linear-gradient(90deg, #00f2fe, #4facfe)', color: '#002f35', border: 'none', borderRadius: '12px', fontWeight: '900', cursor: 'pointer' }}>{isRegisterMode ? "CREATE ACCOUNT" : "SIGN IN"}</button>
            <div style={{ marginTop: '25px', textAlign: 'center', fontSize: '14px' }}>
              {isRegisterMode ? "Already a Quant?" : "New to the system?"} 
              <span onClick={() => setIsRegisterMode(!isRegisterMode)} style={{ color: '#00f2fe', cursor: 'pointer', marginLeft: '8px', fontWeight: 'bold' }}>{isRegisterMode ? "Login here" : "Register now"}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', backgroundColor: '#f4f7fe', minHeight: '100vh' }}>
      <div style={{ width: '280px', background: '#1e293b', padding: '40px 20px', position: 'fixed', height: '100vh', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <h2 style={{ color: '#00f2fe', fontWeight: '900', marginBottom: '40px' }}>🛡️ QuantShield</h2>
        {["Dashboard", "Analytics", "Stocks", "Monte Carlo","Settings"].map(tab => (
          <div key={tab} onClick={() => setActiveTab(tab)} style={{ background: activeTab === tab ? 'rgba(0, 242, 254, 0.15)' : 'transparent', color: activeTab === tab ? '#00f2fe' : '#94a3b8', padding: '16px 20px', borderRadius: '12px', cursor: 'pointer', borderLeft: activeTab === tab ? '4px solid #00f2fe' : '4px solid transparent' }}>{tab}</div>
        ))}
        <div style={{ position: 'absolute', bottom: '30px', left: '20px', color: '#f85149', cursor: 'pointer' }} onClick={() => setIsLoggedIn(false)}>🔒 Logout</div>
      </div>

      <div style={{ flex: 1, padding: '40px 50px', marginLeft: '280px' }}>
        {activeTab === "Dashboard" && data && (
          <div id="report-area">
             <div style={{ background: '#1e293b', padding: '20px', borderRadius: '20px', marginBottom: '25px', display: 'flex', gap: '15px' }}>
                <select value={selectedStock} onChange={(e) => setSelectedStock(e.target.value)} style={{ background: '#0f172a', color: '#00f2fe', padding: '10px', borderRadius: '10px' }}>
                  {stockList.map(s => <option key={s.symbol} value={s.symbol}>{s.name}</option>)}
                </select>
                <button onClick={speakStatus} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '20px' }}>🔊</button>
                <button onClick={downloadReport} style={{ marginLeft: 'auto', padding: '10px 20px', background: '#4facfe', borderRadius: '10px', border: 'none', fontWeight: 'bold' }}>📥 Report</button>
             </div>
             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px' }}>
                <MiniCard title="MARKET PRICE" value={`₹${livePrice.toFixed(2)}`} color="#3b82f6" />
                <MiniCard title="BSI SCORE" value={`${data.bsi_score}%`} color="#00f2fe" />
                <MiniCard title="DECISION" value={data.decision} color="#10b981" />
                <MiniCard title="WALLET" value={`₹${wallet.toLocaleString()}`} color="#f59e0b" />
             </div>
             <div style={{ background: '#1e293b', padding: '20px', borderRadius: '20px', marginTop: '20px', height: '300px' }}>
                <Line data={liveGraphData} options={{ maintainAspectRatio: false }} />
             </div>
             <div style={{ marginTop: '20px', display: 'flex', gap: '15px' }}>
                <button onClick={() => executeTrade("BUY")} style={{ flex: 1, padding: '15px', background: '#10b981', border: 'none', borderRadius: '10px', color: 'white', fontWeight: 'bold' }}>BUY 1 UNIT</button>
                <button onClick={() => executeTrade("SELL")} style={{ flex: 1, padding: '15px', background: '#ef4444', border: 'none', borderRadius: '10px', color: 'white', fontWeight: 'bold' }}>SELL ALL</button>
             </div>
          </div>
        )}
        {activeTab === "Settings" && (
           <div style={{ background: 'white', padding: '30px', borderRadius: '20px' }}>
              <h3>System Settings</h3>
              <p>WhatsApp Alerts: <span style={{ color: isWhatsappEnabled ? 'green' : 'red' }}>{isWhatsappEnabled ? 'ON' : 'OFF'}</span></p>
              <button onClick={() => setIsWhatsappEnabled(!isWhatsappEnabled)}>Toggle WhatsApp</button>
           </div>
        )}
      </div>
    </div>
  );
}

function MiniCard({ title, value, color }) {
  return (
    <div style={{ background: 'white', padding: '20px', borderRadius: '20px', borderLeft: `6px solid ${color}`, boxShadow: '0 4px 10px rgba(0,0,0,0.05)' }}>
      <div style={{ color: '#64748b', fontSize: '11px', fontWeight: 'bold' }}>{title}</div>
      <div style={{ fontSize: '20px', fontWeight: '800' }}>{value}</div>
    </div>
  );
}

export default App;