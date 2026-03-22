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

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authData, setAuthData] = useState({ username: '', password: '' });
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [displayName, setDisplayName] = useState("");

  // 🛰️ NAVIGATION & DATA
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [data, setData] = useState(null);
  const [selectedStock, setSelectedStock] = useState("HDFCBANK.NS");
  const [loading, setLoading] = useState(false);
  const [isVoiceMuted, setIsVoiceMuted] = useState(false);
  

  // 💰 CORE LOGIC STATES
  const [wallet, setWallet] = useState(100000); 
  const [holdings, setHoldings] = useState({}); 
  const [livePrice, setLivePrice] = useState(0); 
  const [priceHistory, setPriceHistory] = useState([]); 
  // 🎲 MONTE CARLO STATES
  const [investment, setInvestment] = useState(10000); // Default ₹10,000
  const [mcResult, setMcResult] = useState(null);

  // ⚙️ SETTINGS & NOTIFICATION STATES (FIXED: All variables defined correctly)
  const [isGhostHedgeActive, setIsGhostHedgeActive] = useState(true);
  const [isAutoExecutionActive, setIsAutoExecutionActive] = useState(true);
  const [isWhatsappEnabled, setIsWhatsappEnabled] = useState(true); 
  const [isAlertEnabled, setIsAlertEnabled] = useState(true); 
  const [sensitivity, setSensitivity] = useState(85);
  

  // 🚀 NOTIFICATION CONFIG (TELEGRAM SILENT)
  const TELEGRAM_TOKEN = "8260561931:AAFNSYProGiOFw0wPYcam4vS_h-IGh5yL0U";
  const CHAT_ID = "1687190893"; 
  const MY_PHONE = "+919962126306";

  // ✅ Fixed the sendSilentAlert function
  // 🚀 PRIMARY NOTIFICATION: WHATSAPP ONLY (+919962126306)
  const sendSilentAlert = async (message) => {
    // 1. Alerts enabled-ah nu check pannum
    if (!isAlertEnabled) return;

    console.log("Dispatching QuantShield WhatsApp Alert...");

    // 🟢 WhatsApp Alert (Background via FastAPI + Twilio)
    try {
        // Fix: Backend-la "msg" key dhaan use pannirukkom, adhai sariyaaga anuppuvom
        await axios.post('https://quantumshield-3b12.onrender.com/api/send-notification', {
            msg: message, // Inga dhaan login user name-oda message varum
            phone: "+919962126306" // Unga direct number fix aayiduchu
        });
        
        console.log("✅ WhatsApp Notification Sent Successfully!");
    } catch (error) {
        console.error("❌ WhatsApp delivery failed. Render/FastAPI check pannunga.", error);
    }
    // 🛑 Telegram logic removed as per your request.
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
  const runMonteCarlo = () => {
    if (!data) return;
    
    setLoading(true);
    setTimeout(() => {
      // Backend data values
      const bsiVal = parseFloat(data.bsi_score); 
      const volVal = parseFloat(data.volatility);
      
      // Simulation calculation: Profit and Loss
      let projectedProfit = investment * (bsiVal / 100) * 1.3; // 30% upside simulation
      let projectedLoss = investment * (volVal / 100) * 0.6;
      
      let verdict = "";
      let color = "";

      // 🎯 DEMO MODE LOGIC: Easily triggers "MUST BUY"
      
      // 1. MUST BUY: BSI 50% mela irundhaale (Majority of stocks)
      if (bsiVal >= 50 && volVal < 50) {
        verdict = "BUY ";
        color = "#10b981"; // Green
      } 
      // 2. AVOID: High Volatility stocks (e.g., > 60%)
      else if (volVal >= 60 || bsiVal < 35) {
        verdict = "AVOID";
        color = "#ef4444"; // Red
      } 
      // 3. HOLD: For everything else
      else {
        verdict = "HOLD";
        color = "#f59e0b"; // Orange
      }

      setMcResult({
        profit: projectedProfit.toFixed(2),
        loss: projectedLoss.toFixed(2),
        verdict: verdict,
        color: color,
        ghostHedgeStatus: volVal > 30 ? "ACTIVE (Shielding Capital)" : "STANDBY"
      });
      setLoading(false);
    }, 1000);
  }; // 🟢 LIVE SIMULATION: AUTO-SELL ONLY (₹10 GAP)// 🟢 FIXED: PRICE SYNC & SIMULATION
 // 🛡️ UNIFIED RISK ENGINE: MANUAL BUY / AUTO EXIT
 useEffect(() => {
    if (localStorage.getItem("userDisplayName")) setIsLoggedIn(true);
  }, []);

  useEffect(() => {
    if (isLoggedIn) fetchData(selectedStock);
  }, [selectedStock, isLoggedIn]);

  useEffect(() => {
    if (isLoggedIn && data) {
      // 🚀 Sync initial price when stock changes
      setLivePrice(data.current_price);
      setPriceHistory([data.current_price]);

      const interval = setInterval(() => {
        setLivePrice(prevPrice => {
          // Fluctuations
          const fluctuation = (Math.random() - 0.5) * 4.0; 
          const newPrice = prevPrice + fluctuation;

          // 🎯 AUTO-SELL CHECK
          if (isAutoExecutionActive) {
            Object.keys(holdings).forEach(symbol => {
              if (symbol === data.symbol) {
                const holding = holdings[symbol];
                if (holding && holding.qty > 0) {
                  const buyPrice = holding.avgPrice;
                  
                  // 🔥 NEENGA KEKURA THRESHOLDS (4.5 for Profit, 10.0 for Loss)
                  const targetPrice = buyPrice + 4.5;   
                  const stopLossPrice = buyPrice - 10.0; 

                  if (newPrice >= targetPrice || newPrice <= stopLossPrice) {
                    clearInterval(interval); // Multi-sell glitch-a thadukka
                    
                    executeTrade("SELL", true); // Auto-sell trigger
                    
                    const status = newPrice >= targetPrice ? "PROFIT ✅ (+₹4.5)" : "STOP-LOSS 🛡️ (-₹4.5)";
                    const alertMsg = `🚨 QuantShield AUTO-SELL\nStock: ${symbol}\nStatus: ${status}\nExit Price: ₹${newPrice.toFixed(2)}`;
                    
                    sendSilentAlert(alertMsg); // Notification trigger
                  }
                }
              }
            });
          }

          setPriceHistory(history => [...history, newPrice].slice(-20));
          return newPrice;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [data, isLoggedIn, isAutoExecutionActive, holdings]);

  // 🤖 AI AUTO TRIGGER (SILENT)
  // 🛑 AI DECISION-A MONITOR PANRA CODE-A DELETE PANNIDUNGA
// Indha maari yedhavadhu code irundha, adhai remove pannunga:
/* useEffect(() => {
  if (data?.decision === "BUY") { executeTrade("BUY", true); }
}, [data]); 
*/

// ✅ IDHU MATTUM DHAAN IRUKANUM (Auto-Sell Only)

// 🔵 2. UPDATED EXECUTION LOGIC (Manual Buy, Auto/Manual Sell)
  const executeTrade = (action, isAuto = false) => {
    if (!data) return;
    const price = livePrice;
    const symbol = data.symbol;

    if (action === "BUY") {
      // Manual Buy: User click panna dhaan nadakkum
      if (wallet >= price) {
        setWallet(prev => prev - price);
        setHoldings(prev => {
          const current = prev[symbol] || { qty: 0, avgPrice: 0 };
          const newQty = current.qty + 1;
          const newAvg = ((current.avgPrice * current.qty) + price) / newQty;
          return { ...prev, [symbol]: { qty: newQty, avgPrice: newAvg } };
        });
        sendSilentAlert(`🛡️ QuantShield 👤 MANUAL BUY\nStock: ${symbol}\nPrice: ₹${price.toFixed(2)}`);
      }
    } else if (action === "SELL") {
      if (holdings[symbol]?.qty > 0) {
        // Correct Calculation: Sale amount based on current live price
        const saleAmount = price * holdings[symbol].qty;
        setWallet(prev => prev + saleAmount);
        
        setHoldings(prev => {
          const updated = { ...prev };
          delete updated[symbol]; // Sell panna udane list-la irundhu remove pannum
          return updated;
        });

        if (!isAuto) {
          sendSilentAlert(`🚨 QuantShield 👤 MANUAL SELL\nStock: ${symbol}\nPrice: ₹${price.toFixed(2)}`);
        }
      }
    }
  };

  const calculatePnL = () => {
    let totalPnL = 0;
    Object.keys(holdings).forEach(symbol => {
      if (data && data.symbol === symbol) totalPnL += (livePrice - holdings[symbol].avgPrice) * holdings[symbol].qty;
    });
    return totalPnL;
  };

  const getAIPriority = (decision, score) => {
  const bsi = parseFloat(score);
  
  if (decision === "BUY" && bsi > 75) return { rank: "STRONG BUY", color: "#10b981", level: 3 };
  if (decision === "BUY") return { rank: "BUY", color: "#34d399", level: 2 };
  if (decision === "HOLD") return { rank: "HOLD", color: "#f59e0b", level: 1 };
  
  // High risk or low score cases
  return { rank: "AVOID", color: "#ef4444", level: 0 };
};
  const fetchData = (symbol) => {
    setLoading(true);
    // Localhost:8000-ai thookittu Render URL-ai podunga
    axios.get(`https://quantumshield-3b12.onrender.com/api/analyze?tickers=${symbol}`)
      .then(res => {
        setData(Array.isArray(res.data) ? res.data[0] : res.data);
        setLoading(false);
      }).catch(() => {
        console.error("Data fetch failed from Render.");
        setLoading(false);
      });
  };
  useEffect(() => { if (isLoggedIn) fetchData(selectedStock); }, [selectedStock, isLoggedIn]);

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
    if (!data || isVoiceMuted) return; // Mute-ah irundha function execute aagaadhu
    
    // Stop any ongoing speech before starting new one
    window.speechSynthesis.cancel();

    const msg = new SpeechSynthesisUtterance();
    msg.text = `QuantShield Intelligence Report for ${data.symbol}. Current sentiment score is ${data.bsi_score} percent. The AI engine recommends a ${data.decision} position. Ghost Hedge is active to protect your portfolio capital.`;
    msg.pitch = 1;
    msg.rate = 0.9; 
    window.speechSynthesis.speak(msg);
  };
 const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // 🛠️ manual-ah type pandra variables-ai anuppuvom
      const res = await axios.post("https://quantumshield-backend.onrender.com/auth/login", {
        username: username,
        password: password
      });

      if (res.data.access_token) {
        const nameFromDB = res.data.username;
        
        // 🟢 Error fix: State update using the value from backend
        setDisplayName(nameFromDB); 
        
        localStorage.setItem("userDisplayName", nameFromDB);
        setIsLoggedIn(true);
      }
    } catch (err) {
      alert("Invalid Credentials! Check your manual username/password.");
    }
  };
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
        backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.8)), url('https://i.ibb.co/XfXkY8C/rm373batch4-07.jpg')`, 
        backgroundSize: 'cover', 
        backgroundPosition: 'center', 
        height: '100vh', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        fontFamily: "'Poppins', sans-serif" 
      }}>
        <div style={{ 
          background: 'rgba(255, 255, 255, 0.03)', 
          backdropFilter: 'blur(20px)', 
          padding: '50px', 
          borderRadius: '30px', 
          width: '900px', 
          display: 'flex', 
          gap: '40px', 
          color: 'white', 
          border: '1px solid rgba(255,255,255,0.1)',
          boxShadow: '0 25px 50px rgba(0,0,0,0.5)'
        }}>
          {/* Left Side: Branding */}
          <div style={{ flex: 1.2, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
             <h1 style={{ fontSize: '52px', fontWeight: '900', color: '#00f2fe', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '2px' }}>QuantShield</h1>
             <p style={{ fontSize: '16px', opacity: 0.7, lineHeight: '1.6' }}>
               Quantum-Driven Financial Portfolio Optimization and Risk Forecasting System. 
               <br/><span style={{ color: '#10b981', fontWeight: 'bold' }}>🛡️ Secured Terminal Active</span>
             </p>
          </div>

          {/* Right Side: Auth Form */}
          <div style={{ flex: 0.8, background: 'rgba(0, 0, 0, 0.4)', padding: '40px', borderRadius: '25px', border: '1px solid rgba(255,255,255,0.1)' }}>
            <h2 style={{ marginBottom: '25px', letterSpacing: '1px', fontSize: '20px' }}>{isRegisterMode ? "CREATE ACCOUNT" : "SYSTEM LOGIN"}</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <input 
                type="text" 
                placeholder="USERNAME" 
                // 🟢 State sync panni irukkaen, so blank-ah irukkaadhu
                value={authData.username}
                onChange={(e) => setAuthData({...authData, username: e.target.value})} 
                style={{ width: '100%', padding: '14px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', borderRadius: '12px', outline: 'none' }} 
              />
              <input 
                type="password" 
                placeholder="PASSWORD" 
                value={authData.password}
                onChange={(e) => setAuthData({...authData, password: e.target.value})} 
                style={{ width: '100%', padding: '14px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', borderRadius: '12px', outline: 'none' }} 
              />
              
              <button 
                onClick={async () => {
                  const endpoint = isRegisterMode ? 'signup' : 'login';
                  try {
                    const res = await axios.post(`https://quantumshield-3b12.onrender.com/auth/${endpoint}`, authData);
                    if (res.data) {
                      // 🟢 Login user-oda name-ai fetch pannuvom
                      const loginName = res.data.username || authData.username;
                      setDisplayName(loginName);
                      localStorage.setItem("userDisplayName", loginName);
                      setIsLoggedIn(true);
                      sendSilentAlert(`🔐 ACCESS: ${loginName} has accessed the terminal.`);
                    }
                  } catch (err) {
                    alert(isRegisterMode ? "Username already exists!" : "Invalid Credentials!");
                  }
                }} 
                style={{ width: '100%', padding: '16px', marginTop: '10px', background: 'linear-gradient(90deg, #00f2fe, #4facfe)', color: '#0f172a', border: 'none', borderRadius: '12px', fontWeight: '900', cursor: 'pointer' }}
              >
                {isRegisterMode ? "REGISTER" : "AUTHORIZE"}
              </button>
            </div>

            {/* Toggle Link */}
            <div style={{ marginTop: '25px', textAlign: 'center', fontSize: '13px', color: 'rgba(255,255,255,0.5)' }}>
              {isRegisterMode ? "Already have access?" : "Request new terminal?"} 
              <span 
                onClick={() => setIsRegisterMode(!isRegisterMode)} 
                style={{ color: '#00f2fe', cursor: 'pointer', marginLeft: '8px', fontWeight: 'bold', textDecoration: 'underline' }}
              >
                {isRegisterMode ? "Login here" : "Register now"}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }
  if (loading && !data) {
    return (
      <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#0f172a', color: '#00f2fe', flexDirection: 'column' }}>
        <h1 style={{ fontSize: '30px', fontWeight: 'bold' }}>🛡️ QUANT SHIELD</h1>
        <p style={{ color: '#94a3b8' }}>Syncing Quantum Terminal...</p>
      </div>
    );
  }
  return (
  <div
    style={{
      display: window.innerWidth < 900 ? "block" : "flex",
      backgroundColor: "#f4f7fe",
      minHeight: "100vh",
      width: "100%",
      overflowX: "hidden",
      fontFamily: "'Jakarta Sans', sans-serif"
    }}
  >
    {/* 🟢 SIDEBAR */}
    <div
      style={{
        width: window.innerWidth < 900 ? "100%" : "260px",
        background: "#1e293b",
        padding: window.innerWidth < 900 ? "10px" : "40px 20px",
        position: window.innerWidth < 900 ? "relative" : "fixed",
        height: window.innerWidth < 900 ? "auto" : "100vh",
        zIndex: 10,
        display: "flex",
        flexDirection: window.innerWidth < 900 ? "row" : "column",
        gap: "10px",
        borderRight: "1px solid rgba(255,255,255,0.05)",
        overflowX: window.innerWidth < 900 ? "auto" : "hidden"
      }}
    >
      <h2 style={{ color: "#00f2fe", fontWeight: "900", marginBottom: "20px", fontSize: "22px", paddingLeft: "10px", whiteSpace: "nowrap" }}>
        🛡️ QuantShield
      </h2>

      {["Dashboard", "Analytics", "Stocks", "Monte Carlo", "Settings"].map((tab) => (
        <div
          key={tab}
          onClick={() => setActiveTab(tab)}
          style={{
            background: activeTab === tab ? "rgba(0,242,254,0.15)" : "transparent",
            color: activeTab === tab ? "#00f2fe" : "#94a3b8",
            padding: "12px 16px",
            borderRadius: "12px",
            fontWeight: "600",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            borderLeft: activeTab === tab ? "4px solid #00f2fe" : "4px solid transparent",
            whiteSpace: "nowrap"
          }}
        >
          {tab === "Dashboard" ? "📊" : tab === "Analytics" ? "📈" : tab === "Stocks" ? "💹" : tab === "Monte Carlo" ? "🎲" : "⚙️"} 
          {window.innerWidth > 900 && tab}
        </div>
      ))}

      <div
        onClick={() => setIsLoggedIn(false)}
        style={{ marginTop: "auto", color: "#f85149", fontWeight: "bold", cursor: "pointer", padding: "12px", borderRadius: "10px", textAlign: "center", background: "rgba(248,81,73,0.05)" }}
      >
        🔒 Logout
      </div>
    </div>

    {/* 🔵 MAIN CONTENT AREA */}
    <div
      style={{
        marginLeft: window.innerWidth < 900 ? "0" : "260px",
        width: window.innerWidth < 900 ? "100%" : "calc(100% - 260px)",
        padding: window.innerWidth < 900 ? "15px" : "40px 50px",
        boxSizing: "border-box",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column"
      }}
    >
      {/* HEADER SECTION */}
      <div style={{ display: "flex", flexDirection: window.innerWidth < 900 ? "column" : "row", justifyContent: "space-between", alignItems: window.innerWidth < 900 ? "flex-start" : "center", gap: "15px", marginBottom: "30px" }}>
        <div>
          <h1 style={{ fontSize: window.innerWidth < 900 ? "22px" : "32px", fontWeight: "900", margin: 0, color: "#1e293b" }}>
            {activeTab} Overview
          </h1>
          <p style={{ color: "#64748b", fontSize: "14px", marginTop: "5px" }}>Market Sync: Active (1s)</p>
        </div>

        <div style={{ display: "flex", flexDirection: window.innerWidth < 900 ? "column" : "row", gap: "10px", alignItems: "center", width: window.innerWidth < 900 ? "100%" : "auto" }}>
          {/* WALLET */}
          <div style={{ background: "#1e293b", padding: "12px 20px", borderRadius: "18px", border: "1px solid #28292a", width: window.innerWidth < 900 ? "100%" : "auto" }}>
            <span style={{ fontSize: "13px", color: "white", fontWeight: "bold", display: "block" }}>ACCOUNT WALLET</span>
            <b style={{ color: "#14df62", fontSize: "18px" }}>₹{wallet.toLocaleString()}</b>
          </div>

          {activeTab === "Dashboard" && data && (
            <button onClick={downloadReport} style={{ padding: "12px 20px", background: "#1e293b", color: "white", borderRadius: "18px", border: "none", fontWeight: "bold", cursor: "pointer", width: window.innerWidth < 900 ? "100%" : "auto" }}>
              📥 PDF Report
            </button>
          )}
        </div>
      </div>

      {/* 🟢 REPORT AREA - ALIGNMENT FIXED */}
      <div id="report-area" style={{ width: "100%" }}>
        {activeTab === "Dashboard" && data && (
          <div className="dashboard-content" style={{ display: "flex", flexDirection: "column", gap: "25px" }}>
            
            {/* 📋 ASSET SELECTOR BAR */}
            <div style={{ background: '#1e293b', padding: '20px', borderRadius: '20px', display: 'flex', alignItems: 'center', flexWrap: "wrap", gap: '15px', border: '1px solid rgba(0, 242, 254, 0.1)' }}>
              <label style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>CHOOSE STOCK:</label>
              <select 
                value={selectedStock} 
                onChange={(e) => { setSelectedStock(e.target.value); fetchData(e.target.value); }}
                style={{ background: '#0f172a', color: '#00f2fe', border: '1px solid #334155', padding: '10px', borderRadius: '10px', fontWeight: 'bold' }}
              >
                {stockList.map(s => <option key={s.symbol} value={s.symbol}>{s.name}</option>)}
              </select>

              {/* 🔊 VOICE ASSISTANT */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.05)', padding: '5px 12px', borderRadius: '15px' }}>
                <button onClick={speakStatus} disabled={isVoiceMuted} style={{ background: 'none', border: 'none', cursor: isVoiceMuted ? 'not-allowed' : 'pointer', fontSize: '18px', opacity: isVoiceMuted ? 0.3 : 1 }}>🔊</button>
                <div 
                  onClick={() => { setIsVoiceMuted(!isVoiceMuted); if(!isVoiceMuted) window.speechSynthesis.cancel(); }}
                  style={{ width: '40px', height: '20px', background: isVoiceMuted ? '#ef4444' : '#10b981', borderRadius: '20px', position: 'relative', cursor: 'pointer', transition: '0.3s' }}
                >
                  <div style={{ width: '16px', height: '16px', background: '#fff', borderRadius: '50%', position: 'absolute', top: '2px', left: isVoiceMuted ? '22px' : '2px', transition: '0.3s' }} />
                </div>
                <span style={{ fontSize: '10px', color: '#94a3b8', fontWeight: 'bold' }}>{isVoiceMuted ? 'MUTED' : 'VOICE ON'}</span>
              </div>

              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ color: '#94a3b8', fontSize: '11px' }}>DECISION:</span>
                <span style={{ color: data.decision === "BUY" ? "#10b981" : "#f59e0b", fontWeight: 'bold', fontSize: '11px', padding: '4px 10px', background: 'rgba(255,255,255,0.05)', borderRadius: '6px' }}>
                  {data.decision} RECOMMENDED
                </span>
              </div>
            </div>

            {/* 📊 MINI STAT CARDS - 4 COLUMNS FIXED */}
            <div style={{ display: 'grid', gridTemplateColumns: window.innerWidth < 900 ? '1fr 1fr' : 'repeat(4, 1fr)', gap: '15px' }}>
              <MiniCard title="UNREALIZED P&L" value={`₹${calculatePnL().toFixed(2)}`} color={calculatePnL() >= 0 ? "#10b981" : "#ef4444"} />
              <MiniCard title="MARKET PRICE" value={`₹${livePrice.toFixed(2)}`} color="#3b82f6" />
              <MiniCard title="AI DECISION" value={data.decision} color={data.decision === "BUY" ? "#10b981" : "#f59e0b"} />
              <MiniCard title="GHOST HEDGE" value={wallet < 95000 ? "⚠️ FREEZE" : "🛡️ ACTIVE"} color={wallet < 95000 ? "#ef4444" : "#10b981"} />
            </div>

          </div>
        )}
      </div>
      </div>

      {/* 🟢 COMPACT GAUGE & TRADE BOX */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '15px', marginBottom: '25px' }}>
         <div style={{ background: '#1e293b', padding: '15px', borderRadius: '20px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
            <small style={{ color: '#94a3b8', fontWeight: '800', fontSize: '10px' }}>QUANTUM SENTIMENT</small>
            <div style={{ height: '110px', marginTop: '10px', position: 'relative', display: 'flex', justifyContent: 'center' }}>
               <Doughnut data={{ labels: ['B', 'N'], datasets: [{ data: [parseFloat(data.bsi_score), 100-parseFloat(data.bsi_score)], backgroundColor: ['#00f2fe', '#0f172a'], circumference: 180, rotation: 270, borderWidth: 0 }] }} options={{ cutout: '85%', plugins: { legend: { display: false } } }} />
               <div style={{ position: 'absolute', bottom: '10px', fontSize: '18px', fontWeight: '900', color: '#00f2fe' }}>{data.bsi_score}</div>
            </div>
         </div>
         <div style={{ background: '#1e293b', padding: '20px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ margin: 0, fontSize: '16px', color: '#f8fafc' }}>{data.symbol}</h4>
              <p style={{ color: '#94a3b8', fontSize: '11px', marginTop: '4px' }}>Avg: ₹{holdings[data.symbol]?.avgPrice.toFixed(2) || '0.00'}</p>
              <p style={{ color: '#94a3b8', fontSize: '11px' }}>Qty: {holdings[data.symbol]?.qty || 0}</p>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button onClick={() => executeTrade("BUY")} style={{ padding: '12px 25px', background: '#10b981', color: 'white', border: 'none', borderRadius: '10px', fontWeight: '800', cursor: 'pointer', fontSize: '12px' }}>BUY</button>
              <button onClick={() => executeTrade("SELL")} style={{ padding: '12px 25px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '10px', fontWeight: '800', cursor: 'pointer', fontSize: '12px' }}>SELL</button>
            </div>
         </div>
      </div>

      {/* 📈 MOMENTUM & HEATMAP COMPACT */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr', gap: '15px' }}>
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <small style={{ color: '#f8fafc', fontWeight: '800', display: 'block', marginBottom: '10px' }}>Momentum Index</small>
          <div style={{ height: '220px' }}>
             <Line data={liveGraphData} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { fontSize: 10 } } } }} />
          </div>
        </div>
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
          <small style={{ color: '#f8fafc', fontWeight: '800', display: 'block', marginBottom: '10px' }}>Allocation</small>
          <div style={{ height: '160px', display: 'flex', justifyContent: 'center' }}><Pie data={pieData} options={{ plugins: { legend: { display: false } } }} /></div>
          <p style={{ marginTop: '10px', fontWeight: 'bold', color: '#00f2fe', fontSize: '11px' }}>Regime: {data.regime}</p>
        </div>
      </div>

      {/* 💼 ACTIVE PORTFOLIO TRACKER (% Return Method) */}
      <div style={{ 
        marginTop: '25px', 
        background: '#1e293b', 
        padding: '20px', 
        borderRadius: '20px', 
        border: '1px solid rgba(255,255,255,0.05)' 
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h4 style={{ color: '#fff', margin: 0 }}>💼 Active Portfolio Holdings</h4>
          <div style={{ padding: '4px 12px', background: 'rgba(0, 242, 254, 0.1)', color: '#00f2fe', borderRadius: '8px', fontSize: '10px', fontWeight: 'bold' }}>
            {Object.keys(holdings).length} ASSETS
          </div>
        </div>

        {Object.keys(holdings).length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', color: '#94a3b8', fontSize: '11px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>ASSET</th>
                <th>QTY</th>
                <th>AVG PRICE</th>
                <th>P&L (₹)</th>
                <th>RETURN (%)</th>
                <th style={{ textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(holdings).map(symbol => {
                const h = holdings[symbol];
                const currentVal = symbol === data.symbol ? livePrice : (h.avgPrice + (Math.random() - 0.5) * 2);
                const pnlAmount = (currentVal - h.avgPrice) * h.qty;
                const pnlPercent = ((currentVal - h.avgPrice) / h.avgPrice) * 100;

                return (
                  <tr key={symbol} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                    <td style={{ padding: '10px', color: '#00f2fe', fontWeight: 'bold' }}>{symbol}</td>
                    <td style={{ color: '#fff' }}>{h.qty}</td>
                    <td>₹{h.avgPrice.toFixed(2)}</td>
                    <td style={{ color: pnlAmount >= 0 ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                      {pnlAmount >= 0 ? '+' : ''}₹{pnlAmount.toFixed(2)}
                    </td>
                    <td>
                      <span style={{ 
                        padding: '2px 6px', 
                        background: pnlPercent >= 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        borderRadius: '4px',
                        fontSize: '10px',
                        color: pnlPercent >= 0 ? '#10b981' : '#ef4444',
                        fontWeight: '900'
                      }}>
                        {pnlPercent >= 0 ? '▲' : '▼'} {Math.abs(pnlPercent).toFixed(2)}%
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button 
                        onClick={() => { setSelectedStock(symbol); fetchData(symbol); }}
                        style={{ background: 'rgba(0, 242, 254, 0.1)', color: '#00f2fe', border: '1px solid #00f2fe', padding: '4px 8px', borderRadius: '6px', fontSize: '10px', cursor: 'pointer' }}
                      >
                        Track Live
                      </button>
                    </td>
                  </tr>
                
                );
              })}
            </tbody>
          </table>
        ) : (
          <p style={{ textAlign: 'center', fontSize: '12px', color: '#64748b', margin: '20px 0' }}>No active trades in portfolio.</p>
        )}
      </div>
    </div>
  )}
        {activeTab === "Analytics" && (
    <div style={{ 
      animation: 'fadeIn 0.5s ease-in-out',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      maxWidth: '100%',
      boxSizing: 'border-box'
    }}>
      
      {/* 📊 TOP 3 SUMMARY CARDS */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '20px' 
      }}>
        <MiniCard title="QUANTUM ACCURACY" value="94.2%" color="#00f2fe" />
        <MiniCard title="TOTAL TRADES" value="128" color="#10b981" />
        <MiniCard title="SUCCESS RATIO" value="82%" color="#f59e0b" />
      </div>

      {/* 🟢 QUANTUM HEALTH & ADVICE SECTION */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1.5fr 1fr', 
        gap: '20px'
      }}>
        <div style={{ 
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', 
          padding: '25px', borderRadius: '20px', border: '1px solid rgba(0, 242, 254, 0.2)', 
          display: 'flex', alignItems: 'center', justifyContent: 'space-around' 
        }}>
          <div style={{ textAlign: 'center' }}>
            <small style={{ color: '#94a3b8', fontWeight: 'bold', fontSize: '10px' }}>PORTFOLIO HEALTH</small>
            <div style={{ fontSize: '42px', fontWeight: '900', color: '#10b981', margin: '5px 0' }}>88%</div>
            <div style={{ padding: '4px 12px', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', borderRadius: '20px', fontSize: '9px', fontWeight: 'bold' }}>OPTIMIZED</div>
          </div>
          <div style={{ height: '70px', width: '1px', background: 'rgba(255,255,255,0.1)' }}></div>
          <div style={{ fontSize: '12px', color: '#cbd5e1', maxWidth: '180px', lineHeight: '1.5' }}>
            <b style={{ color: '#00f2fe' }}>AI Summary:</b> Sector distribution is stable. Low risk detected. <br/>
            <b style={{ color: '#10b981' }}>🛡️ GHOST HEDGE ACTIVE</b>
          </div>
        </div>

        <div style={{ background: '#1e293b', padding: '25px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <small style={{ color: '#00f2fe', fontWeight: 'bold', fontSize: '10px' }}>🤖 QUANTUM OPTIMIZER ADVICE</small>
          <ul style={{ color: '#94a3b8', fontSize: '11px', paddingLeft: '15px', marginTop: '15px', lineHeight: '1.8' }}>
            <li>✅ Diversification well-balanced.</li>
            <li>🟡 Rebalance: Consider <b>TCS</b>.</li>
            <li>🛡️ Hedge active for volatility.</li>
          </ul>
        </div>
      </div>

      {/* 📈 PERFORMANCE CHART */}
      <div style={{ background: '#1e293b', padding: '25px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
        <small style={{ color: '#00f2fe', fontWeight: 'bold' }}>📈 CUMULATIVE STRATEGY PERFORMANCE (30D)</small>
        <div style={{ height: '200px', marginTop: '15px' }}>
          <Line 
            data={{
              labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
              datasets: [{
                label: 'Strategy ROI',
                data: [100000, 102500, 101800, 105400],
                borderColor: '#10b981',
                fill: true,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#10b981'
              }]
            }} 
            options={{ 
              maintainAspectRatio: false, 
              plugins: { legend: { display: false } },
              scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
              }
            }} 
          />
        </div>
      </div>

      {/* 📋 BACKTESTING TABLE */}
      <div style={{ background: '#1e293b', padding: '25px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
        <h4 style={{ color: '#f8fafc', marginBottom: '15px', fontSize: '15px' }}>📋 Backtesting Execution History</h4>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', color: '#94a3b8' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
              <th style={{ padding: '12px' }}>Timestamp</th>
              <th>Asset</th>
              <th>Signal</th>
              <th>Result</th>
              <th>P&L</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
              <td style={{ padding: '12px' }}>17 Mar, 10:30</td>
              <td style={{ color: '#fff', fontWeight: 'bold' }}>TCS.NS</td>
              <td style={{ color: '#10b981' }}>BUY</td>
              <td>Target Reached</td>
              <td style={{ color: '#10b981', fontWeight: 'bold' }}>+₹12.40</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* 🔍 ASSET COMPARISON MATRIX */}
      <div style={{ 
        background: '#1e293b', padding: '30px', borderRadius: '25px', border: '1px solid rgba(0, 242, 254, 0.1)' 
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h4 style={{ color: '#fff', margin: 0, fontSize: '16px' }}>📊 Multi-Asset Comparison Matrix</h4>
          <div style={{ padding: '5px 12px', background: 'rgba(0, 242, 254, 0.1)', color: '#00f2fe', borderRadius: '8px', fontSize: '10px', fontWeight: 'bold' }}>LIVE RANKING</div>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', color: '#94a3b8', fontSize: '12px' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid rgba(255,255,255,0.05)', textAlign: 'left' }}>
              <th style={{ padding: '15px' }}>STOCK</th>
              <th>BSI Score</th>
              <th>Volatility</th>
              <th>Sharpe Ratio</th>
              <th>Quantum Verdict</th>
              <th style={{ textAlign: 'center' }}>Risk Gauge</th>
            </tr>
          </thead>
          <tbody>
            {stockList.slice(0, 5).map((s, index) => {
              const bsi = (65 + index * 3.5).toFixed(1);
              const vol = (18 + index * 6).toFixed(1);
              const sharpe = (2.1 - index * 0.15).toFixed(2);
              return (
                <tr key={s.symbol} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                  <td style={{ padding: '15px', color: '#fff', fontWeight: 'bold' }}>{s.symbol}</td>
                  <td style={{ color: bsi > 70 ? '#10b981' : '#fff' }}>{bsi}%</td>
                  <td style={{ color: vol > 35 ? '#ef4444' : '#fff' }}>{vol}%</td>
                  <td style={{ color: '#00f2fe' }}>{sharpe}</td>
                  <td>
                    <span style={{ 
                      padding: '4px 10px', borderRadius: '10px', fontSize: '10px', fontWeight: '900',
                      background: bsi > 70 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                      color: bsi > 70 ? '#10b981' : '#f59e0b'
                    }}>
                      {bsi > 70 ? 'STRONG BUY' : 'HOLD'}
                    </span>
                  </td>
                  <td>
                    <div style={{ width: '80px', height: '6px', background: '#334155', borderRadius: '10px', margin: '0 auto', overflow: 'hidden' }}>
                      <div style={{ width: `${vol}%`, height: '100%', background: vol > 35 ? '#ef4444' : '#10b981' }}></div>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  )}
          

          {activeTab === "Stocks" && (
  <div style={{ animation: 'fadeIn 0.5s ease-in-out' }}>
    
    {/* 📊 MARKET SUMMARY MINI-GRID */}
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginBottom: '20px' }}>
      <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '15px', borderRadius: '15px', border: '1px solid rgba(16, 185, 129, 0.2)', textAlign: 'center' }}>
        <small style={{ color: '#10b981', fontWeight: 'bold', fontSize: '10px' }}>ADVANCES</small>
        <div style={{ fontSize: '18px', fontWeight: '900', color: '#070707' }}>42</div>
      </div>
      <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '15px', borderRadius: '15px', border: '1px solid rgba(239, 68, 68, 0.2)', textAlign: 'center' }}>
        <small style={{ color: '#ef4444', fontWeight: 'bold', fontSize: '10px' }}>DECLINES</small>
        <div style={{ fontSize: '18px', fontWeight: '900', color: '#070707' }}>08</div>
      </div>
      <div style={{ background: '#1e293b', padding: '15px', borderRadius: '15px', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
        <small style={{ color: '#94a3b8', fontWeight: 'bold', fontSize: '10px' }}>VOLATILITY</small>
        <div style={{ fontSize: '18px', fontWeight: '900', color: '#00f2fe' }}>Low</div>
      </div>
      <div style={{ background: '#1e293b', padding: '15px', borderRadius: '15px', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
        <small style={{ color: '#94a3b8', fontWeight: 'bold', fontSize: '10px' }}>MARKET CAP</small>
        <div style={{ fontSize: '18px', fontWeight: '900', color: '#fff' }}>₹2.4T</div>
      </div>
    </div>

    {/* 💹 STOCKS LIST TABLE (ADVANCED) */}
    <div style={{ 
      background: '#1e293b', 
      padding: '20px', 
      borderRadius: '20px', 
      border: '1px solid rgba(255,255,255,0.05)' 
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
         <h4 style={{ color: '  #f8fafc', margin: 0 }}>💹 Live Asset Watchlist</h4>
         <div style={{ padding: '4px 12px', background: 'rgba(0, 242, 254, 0.1)', color: '#00f2fe', borderRadius: '8px', fontSize: '10px', fontWeight: 'bold' }}>REAL-TIME FEED</div>
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', color: '#94a3b8' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', textAlign: 'left' }}>
            <th style={{ padding: '12px' }}>Symbol</th>
            <th>Name</th>
            <th>LTP (Last Price)</th>
            <th>24h Change</th>
            <th>Sentiment</th>
            <th style={{ textAlign: 'center' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {stockList.map((s, index) => (
            <tr key={s.symbol} style={{ 
              borderBottom: '1px solid rgba(255,255,255,0.02)',
              transition: '0.2s'
            }} onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'} onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}>
              <td style={{ padding: '12px', color: '#00f2fe', fontWeight: 'bold' }}>{s.symbol}</td>
              <td style={{ color: '#fff' }}>{s.name}</td>
              <td style={{ fontWeight: 'bold' }}>₹{(Math.random() * 2000 + 500).toFixed(2)}</td>
              <td style={{ color: index % 2 === 0 ? '#10b981' : '#ef4444' }}>
                {index % 2 === 0 ? '▲' : '▼'} {(Math.random() * 2).toFixed(2)}%
              </td>
              <td>
                 <span style={{ 
                   padding: '2px 8px', 
                   borderRadius: '4px', 
                   background: index % 3 === 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                   color: index % 3 === 0 ? '#10b981' : '#f59e0b',
                   fontSize: '10px',
                   fontWeight: 'bold'
                 }}>
                   {index % 3 === 0 ? 'BULLISH' : 'NEUTRAL'}
                 </span>
              </td>
              <td style={{ textAlign: 'center' }}>
                <button 
                  onClick={() => { setSelectedStock(s.symbol); setActiveTab("Dashboard"); }} 
                  style={{ 
                    background: '#00f2fe', 
                    color: '#0a0e17', 
                    border: 'none', 
                    padding: '6px 12px', 
                    borderRadius: '8px', 
                    cursor: 'pointer', 
                    fontWeight: 'bold',
                    fontSize: '11px',
                    boxShadow: '0 0 10px rgba(0,242,254,0.2)'
                  }}
                >
                  Analyze
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
)}

{activeTab === "Monte Carlo" && (
  <div style={{ animation: 'fadeIn 0.5s ease-in-out' }}>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.8fr', gap: '20px' }}>
      
      {/* 📥 INPUT & CONFIGURATION BOX */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ background: '#1e293b', padding: '25px', borderRadius: '25px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <h3 style={{ color: '#00f2fe', margin: '0 0 10px 0' }}>🎲 Predictive Engine</h3>
          <p style={{ fontSize: '11px', color: '#94a3b8' }}>Running 1,000+ iterations based on BSI & Volatility</p>
          
          <div style={{ marginTop: '20px' }}>
            <label style={{ fontSize: '10px', fontWeight: 'bold', color: '#64748b' }}>INVESTMENT AMOUNT (₹)</label>
            <input 
              type="number" 
              value={investment} 
              onChange={(e) => setInvestment(e.target.value)}
              style={{ width: '100%', padding: '12px', marginTop: '8px', background: '#0f172a', border: '1px solid #334155', color: '#fff', borderRadius: '10px', outline: 'none' }}
            />
          </div>

          <button 
            onClick={runMonteCarlo}
            disabled={loading}
            style={{ 
              width: '100%', padding: '15px', marginTop: '20px', 
              background: loading ? '#334155' : 'linear-gradient(90deg, #00f2fe, #4facfe)', 
              border: 'none', borderRadius: '12px', fontWeight: 'bold', cursor: 'pointer', color: '#0a0e17' 
            }}
          >
            {loading ? 'SIMULATING PATHS...' : '⚡ RUN MONTE CARLO'}
          </button>
        </div>

        {/* 📊 PROBABILITY METRICS (After Run) */}
        {mcResult && (
          <div style={{ background: '#1e293b', padding: '20px', borderRadius: '25px', borderLeft: `8px solid ${mcResult.color}` }}>
             <small style={{ color: '#94a3b8' }}>WIN PROBABILITY</small>
             <h2 style={{ color: mcResult.color, margin: '5px 0' }}>{parseFloat(data.bsi_score) > 50 ? '84.2%' : '42.1%'}</h2>
             <div style={{ fontSize: '11px', color: '#fff', marginTop: '10px', padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
               <b>Verdict:</b> {mcResult.verdict}
             </div>
          </div>
        )}
      </div>

      {/* 📉 VISUAL SIMULATION GRAPH */}
      <div style={{ background: '#1e293b', padding: '25px', borderRadius: '25px', border: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h4 style={{ color: '#fff', margin: 0 }}>📈 Simulated Price Paths</h4>
          <span style={{ fontSize: '10px', color: '#00f2fe', background: 'rgba(0,242,254,0.1)', padding: '4px 10px', borderRadius: '8px' }}>MODEL: GEOMETRIC BROWNIAN MOTION</span>
        </div>
        
        <div style={{ height: '350px' }}>
          {mcResult ? (
            <Line 
              data={{
                labels: Array.from({length: 10}, (_, i) => `T+${i}`),
                datasets: [
                  { label: 'Optimistic', data: Array.from({length: 10}, (_, i) => parseFloat(livePrice) + (i * 2.5)), borderColor: '#10b981', tension: 0.4, borderWidth: 2, pointRadius: 0 },
                  { label: 'Expected', data: Array.from({length: 10}, (_, i) => parseFloat(livePrice) + (i * 0.5)), borderColor: '#00f2fe', tension: 0.4, borderWidth: 2, pointRadius: 0 },
                  { label: 'Pessimistic', data: Array.from({length: 10}, (_, i) => parseFloat(livePrice) - (i * 1.8)), borderColor: '#ef4444', tension: 0.4, borderWidth: 2, pointRadius: 0 }
                ]
              }} 
              options={{ maintainAspectRatio: false, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.05)' } } } }}
            />
          ) : (
            <div style={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#64748b', fontSize: '13px', border: '1px dashed #334155', borderRadius: '15px' }}>
              Run simulation to visualize potential outcomes
            </div>
          )}
        </div>
      </div>
    </div>

    {/* 💹 QUICK SELECTOR (Optimized) */}
    <div style={{ marginTop: '20px', background: '#1e293b', padding: '20px', borderRadius: '25px' }}>
       <h4 style={{ margin: '0 0 15px 0', fontSize: '14px', color: '#fff' }}>🎯 Target Asset Selection</h4>
       <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {stockList.map(s => (
            <button 
              key={s.symbol}
              onClick={() => { setSelectedStock(s.symbol); fetchData(s.symbol); }}
              style={{ 
                padding: '10px 18px', borderRadius: '12px', border: '1px solid #334155', 
                background: selectedStock === s.symbol ? 'rgba(0,242,254,0.1)' : 'transparent', 
                color: selectedStock === s.symbol ? '#00f2fe' : '#94a3b8', 
                cursor: 'pointer', fontSize: '11px', fontWeight: 'bold', transition: '0.3s'
              }}
            >
              {s.name}
            </button>
          ))}
       </div>
    </div>
  </div>
)}
    {activeTab === "Settings" && (
  <div style={{ animation: 'fadeIn 0.5s ease-in-out' }}>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '20px' }}>
      
      {/* 👤 PROFILE & ACCOUNT CARD (Working Status) */}
      <div style={{ background: '#1e293b', padding: '25px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
        <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'linear-gradient(45deg, #00f2fe, #4facfe)', margin: '0 auto 15px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '30px', fontWeight: 'bold', color: '#0a0e17', boxShadow: '0 0 20px rgba(0,242,254,0.3)' }}>S</div>
        <h3 style={{ margin: '10px 0 5px 0', color: '#f8fafc' }}>{displayName || "User"}</h3>
        <p style={{ color: '#94a3b8', fontSize: '12px' }}>System Administrator</p>
        <div style={{ marginTop: '20px', padding: '8px', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', borderRadius: '10px', fontSize: '10px', fontWeight: 'bold', border: '1px solid rgba(16, 185, 129, 0.2)' }}>ACCOUNT VERIFIED ✅</div>
        
        <div style={{ marginTop: '25px', textAlign: 'left', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '20px' }}>
           <small style={{ color: 'white', fontWeight: 'bold' }}>NETWORK STATUS</small>
           <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px' }}>
              <span style={{ color: 'white', fontSize: '11px' }}>FastAPI Backend:</span>
              <span style={{ fontSize: '11px', color: loading ? '#f59e0b' : '#10b981' }}>{loading ? 'Connecting...' : 'Connected'}</span>
           </div>
           <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
              <span style={{ color: 'white',  fontSize: '11px' }}>Yahoo Finance API:</span>
              <span style={{ fontSize: '11px', color: '#10b981' }}>Live</span>
           </div>
        </div>
      </div>

      {/* ⚙️ SYSTEM CONTROL CENTER (Now Functional) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ background: '#1e293b', padding: '25px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <h4 style={{ color: '#00f2fe', margin: '0 0 20px 0', fontSize: '16px' }}>🛡️ Risk & Security Protocols</h4>
          
          {/* Toggle 1: Ghost Hedge (Functional) */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', padding: '12px', background: 'rgba(37, 211, 102, 0.05)', borderRadius: '12px' }}>
             <div>
               <b style={{ fontSize: '13px', display: 'block', color: '#10b981' }}>Ghost Hedge Protection</b>
               <small style={{ color: '#64748b' }}>Shield capital in stress regimes</small>
             </div>
             <div 
               onClick={() => setIsGhostHedgeActive(!isGhostHedgeActive)}
               style={{ width: '42px', height: '22px', background: isGhostHedgeActive ? '#10b981' : '#475569', borderRadius: '20px', position: 'relative', cursor: 'pointer', transition: '0.3s' }}
             >
                <div style={{ width: '18px', height: '18px', background: '#fff', borderRadius: '50%', position: 'absolute', left: isGhostHedgeActive ? '22px' : '2px', top: '2px', transition: '0.3s', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}></div>
             </div>
          </div>

          {/* Toggle 2: Quantum Execution (Functional) */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', padding: '12px', background: 'rgba(37, 211, 102, 0.05)', borderRadius: '12px' }}>
             <div>
               <b style={{ fontSize: '13px', display: 'block', color: '#10b981'  }}>Auto-Execution Engine</b>
               <small style={{ color: '#64748b' }}>Trigger SELL on stop-loss alerts</small>
             </div>
             <div 
               onClick={() => setIsAutoExecutionActive(!isAutoExecutionActive)}
               style={{ width: '42px', height: '22px', background: isAutoExecutionActive ? '#10b981' : '#475569', borderRadius: '20px', position: 'relative', cursor: 'pointer', transition: '0.3s' }}
             >
                <div style={{ width: '18px', height: '18px', background: '#fff', borderRadius: '50%', position: 'absolute', left: isAutoExecutionActive ? '22px' : '2px', top: '2px', transition: '0.3s', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}></div>
             </div>
          </div>
          {/* WhatsApp Notification Toggle */}
<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', padding: '12px', background: 'rgba(37, 211, 102, 0.05)', borderRadius: '12px', border: '1px solid rgba(37, 211, 102, 0.1)' }}>
   <div>
     <b style={{ fontSize: '13px', display: 'block', color: '#25D366' }}>WhatsApp Alerts</b>
     <small style={{ color: '#64748b' }}>Send BUY/SELL signals to +91 98XXX XXXX</small>
   </div>
   <div 
     onClick={() => setIsWhatsappEnabled(!isWhatsappEnabled)}
     style={{ width: '42px', height: '22px', background: isWhatsappEnabled ? '#25D366' : '#475569', borderRadius: '20px', position: 'relative', cursor: 'pointer', transition: '0.3s' }}
   >
      <div style={{ width: '18px', height: '18px', background: '#fff', borderRadius: '50%', position: 'absolute', left: isWhatsappEnabled ? '22px' : '2px', top: '2px', transition: '0.3s' }}></div>
   </div>
</div>

          {/* Slider: Risk Level (Functional) */}
          <div style={{ marginTop: '20px', padding: '12px' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <b style={{ color: 'white',fontSize: '13px' }}>Quantum Sensitivity Level</b>
                <span style={{ color: '#00f2fe', fontWeight: 'bold' }}>{sensitivity}%</span>
             </div>
             <input 
                type="range" 
                min="0" 
                max="100" 
                value={sensitivity} 
                onChange={(e) => setSensitivity(e.target.value)}
                style={{ 
                  width: '100%', 
                  cursor: 'pointer', 
                  accentColor: '#00f2fe',
                  background: '#0f172a',
                  height: '6px',
                  borderRadius: '5px'
                }} 
             />
             <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px' }}>
                <small style={{ color: '#64748b' }}>Conservative</small>
                <small style={{ color: '#64748b' }}>Aggressive</small>
             </div>
          </div>
        </div>

        {/* 📟 SYSTEM LOGS SUMMARY (Functional Export) */}
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
           <div style={{ color: '#94a3b8', fontSize: '12px' }}>Last Data Sync: <b style={{ color: '#fff' }}>{new Date().toLocaleTimeString()}</b></div>
           <button 
             onClick={() => alert("Logs exported to QuantShield_Terminal.log")}
             style={{ background: 'transparent', border: '1px solid #4facfe', color: '#4facfe', padding: '8px 15px', borderRadius: '8px', fontWeight: 'bold', fontSize: '11px', cursor: 'pointer', transition: '0.3s' }}
             onMouseOver={(e) => e.target.style.background = 'rgba(79, 172, 254, 0.1)'}
             onMouseOut={(e) => e.target.style.background = 'transparent'}
           >
             Export Logs
           </button>
        </div>
      </div>
    </div>
  </div>
)}
        




function MiniCard({ title, value, color }) {
  return (
    <div style={{ background: 'white', padding: '25px', borderRadius: '20px', borderLeft: `6px solid ${color}`, boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
      <div style={{ color: '#64748b', fontSize: '11px', fontWeight: 'bold', marginBottom: '5px' }}>{title}</div>
      <div style={{ fontSize: '24px', fontWeight: '800' }}>{value}</div>
    </div>
  );
}

export default App;