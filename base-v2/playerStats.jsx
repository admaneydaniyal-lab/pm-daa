// Prematch — Player Stats screen

const TABS = ["Overview", "Stats", "Matches", "Career"];

const STAT_ROWS = [
  { label: "Matches Played",   value: "20",   pro: false },
  { label: "Minutes played",   value: "1783", pro: true  },
  { label: "Starting XI",      value: "100%", pro: false },
  { label: "Goals",            value: "29",   pro: false },
  { label: "Minutes per Goal", value: "61",   pro: true  },
  { label: "Assists",          value: "2",    pro: false },
  { label: "Clean sheets",     value: "3",    pro: false },
  { label: "Clean Sheet",      value: "0%",   pro: false },
  { label: "Win",              value: "85%",  pro: false },
  { label: "Top XI",           value: "6",    pro: true  },
];

function ProBadge() {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      background: "#6d28d9", color: "#fff",
      fontSize: 9, fontWeight: 800, letterSpacing: "0.06em",
      borderRadius: 5, padding: "2px 6px",
      marginLeft: 7,
    }}>PRO</span>
  );
}

function HexCheck({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 26 26" fill="none">
      <path d="M13 1 L24 7 L24 19 L13 25 L2 19 L2 7 Z" fill="#c8f135"/>
      <path d="M8.5 13 L11.5 16 L17.5 10"
            stroke="#0d0d0d" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

function JerseyBack() {
  return (
    <svg width="190" height="220" viewBox="0 0 190 220" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Collar */}
      <path d="M75 18 Q95 36 115 18" stroke="rgba(255,255,255,0.12)" strokeWidth="1.5" fill="none"/>
      {/* Left sleeve */}
      <path d="M75 18 L20 55 L38 72 L62 48 L62 185 L128 185 L128 48 L152 72 L170 55 L115 18 Q95 36 75 18 Z"
            fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      {/* Number 9 */}
      <text x="95" y="145" textAnchor="middle"
            fontSize="86" fontWeight="900" letterSpacing="-0.04em"
            fill="rgba(255,255,255,0.88)" fontFamily="Archivo,sans-serif">9</text>
    </svg>
  );
}

function PlayerStats() {
  const [activeTab, setActiveTab] = React.useState("Stats");
  const [scrolled, setScrolled]   = React.useState(false);
  const scrollRef = React.useRef(null);

  React.useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const onScroll = () => setScrolled(el.scrollTop > 110);
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div style={{ position: "absolute", inset: 0, background: "#0d0d0d", display: "flex", flexDirection: "column" }}>

      {/* ── Sticky top nav ── */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, zIndex: 20,
        paddingTop: 54,
        background: scrolled ? "rgba(13,13,13,0.96)" : "transparent",
        backdropFilter: scrolled ? "blur(12px)" : "none",
        transition: "background 250ms",
      }}>
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "6px 16px 10px",
        }}>
          <button style={{
            background: "none", border: "none", color: "#fff", cursor: "pointer",
            padding: "4px 2px", display: "flex", alignItems: "center",
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                 stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5M12 5l-7 7 7 7"/>
            </svg>
          </button>

          <span style={{
            fontWeight: 800, fontSize: 12, color: "#fff",
            letterSpacing: "0.06em", textTransform: "uppercase",
            opacity: scrolled ? 1 : 0,
            transition: "opacity 200ms",
          }}>Rhynell Gordon-Messam</span>

          <button style={{
            background: "none", border: "none", color: "#fff", cursor: "pointer",
            padding: "4px 2px", display: "flex", alignItems: "center",
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                 stroke="#fff" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/>
            </svg>
          </button>
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div ref={scrollRef} className="scroll-area"
           style={{ position: "absolute", inset: 0, overflowY: "auto" }}>

        {/* Hero */}
        <div style={{ position: "relative", paddingTop: 106, paddingBottom: 24, overflow: "hidden" }}>
          {/* Jersey — positioned top-right */}
          <div style={{
            position: "absolute", right: -14, top: 14,
            opacity: 0.9, pointerEvents: "none",
          }}>
            <JerseyBack/>
          </div>

          {/* Name + badge */}
          <div style={{ paddingLeft: 20, paddingRight: 140, position: "relative" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <h1 style={{
                margin: 0,
                fontWeight: 900, fontSize: 38, color: "#fff",
                letterSpacing: "-0.02em", lineHeight: 1.05,
                textTransform: "uppercase",
              }}>
                RHYNELL<br/>GORDON-<br/>MESSAM
              </h1>
              <div style={{ paddingTop: 52 }}>
                <HexCheck size={26}/>
              </div>
            </div>
          </div>

          {/* Position + club pills */}
          <div style={{ display: "flex", gap: 8, marginTop: 18, paddingLeft: 20 }}>
            <span style={{
              border: "1.5px solid rgba(255,255,255,0.28)",
              borderRadius: 999, padding: "5px 13px",
              fontSize: 11, fontWeight: 800, color: "#fff",
              letterSpacing: "0.1em", textTransform: "uppercase",
            }}>STRIKER</span>
            <span style={{
              border: "1.5px solid rgba(255,255,255,0.28)",
              borderRadius: 999, padding: "5px 13px",
              fontSize: 11, fontWeight: 800, color: "#fff",
              letterSpacing: "0.05em",
              display: "inline-flex", alignItems: "center", gap: 5,
            }}>
              AC UNITED FC
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                   stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M7 17L17 7"/><path d="M9 7h8v8"/>
              </svg>
            </span>
          </div>
        </div>

        {/* ── Tabs ── */}
        <div style={{
          display: "flex",
          borderBottom: "1px solid rgba(255,255,255,0.09)",
          paddingLeft: 4,
          position: "sticky", top: 90, zIndex: 10,
          background: "#0d0d0d",
        }}>
          {TABS.map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              background: "none", border: "none", cursor: "pointer",
              padding: "13px 14px 11px",
              fontSize: 14, fontWeight: tab === activeTab ? 700 : 400,
              color: tab === activeTab ? "#fff" : "rgba(255,255,255,0.38)",
              letterSpacing: "-0.01em",
              borderBottom: `2px solid ${tab === activeTab ? "#fff" : "transparent"}`,
              marginBottom: -1,
              transition: "color 180ms",
              fontFamily: "inherit",
            }}>{tab}</button>
          ))}
        </div>

        {/* ── Season Performance card ── */}
        <div style={{
          margin: "14px 14px 10px",
          background: "rgba(255,255,255,0.05)",
          borderRadius: 16, padding: "18px 20px 22px",
        }}>
          <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", letterSpacing: "-0.01em" }}>
            Season Performance
          </div>
          <div style={{
            fontSize: 12, fontWeight: 500, color: "rgba(255,255,255,0.42)",
            marginTop: 4,
          }}>2025/2026 · All competitions</div>

          <div style={{ display: "flex", gap: 36, marginTop: 22 }}>
            {[{ v: "20", l: "Games" }, { v: "29", l: "Goals" }, { v: "2", l: "Assists" }].map(({ v, l }) => (
              <div key={l}>
                <div style={{
                  fontSize: 48, fontWeight: 900, color: "#fff",
                  letterSpacing: "-0.04em", lineHeight: 1,
                  fontVariantNumeric: "tabular-nums",
                }}>{v}</div>
                <div style={{
                  fontSize: 13, color: "rgba(255,255,255,0.48)",
                  marginTop: 7, fontWeight: 400,
                }}>{l}</div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Statistical Breakdown card ── */}
        <div style={{
          margin: "0 14px 40px",
          background: "rgba(255,255,255,0.05)",
          borderRadius: 16, padding: "18px 20px 8px",
        }}>
          <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", letterSpacing: "-0.01em" }}>
            Statistical Breakdown
          </div>

          {/* Filter / Summary row */}
          <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
            <button style={{
              display: "inline-flex", alignItems: "center", gap: 6,
              background: "rgba(255,255,255,0.08)", border: "none", borderRadius: 999,
              padding: "8px 16px", color: "#fff", fontSize: 13, fontWeight: 600,
              cursor: "pointer", fontFamily: "inherit", letterSpacing: "-0.01em",
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                   stroke="#fff" strokeWidth="2" strokeLinecap="round">
                <line x1="3" y1="6"  x2="21" y2="6"/>
                <line x1="7" y1="12" x2="17" y2="12"/>
                <line x1="10" y1="18" x2="14" y2="18"/>
              </svg>
              Filter
            </button>
            <button style={{
              background: "#fff", border: "none", borderRadius: 999,
              padding: "8px 18px", color: "#0d0d0d", fontSize: 13, fontWeight: 700,
              cursor: "pointer", fontFamily: "inherit", letterSpacing: "-0.01em",
            }}>Summary</button>
          </div>

          {/* Section heading */}
          <div style={{ marginTop: 20 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>All competitions</div>
            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.42)", marginTop: 3, fontWeight: 500 }}>
              2025/2026
            </div>
          </div>

          {/* Stat rows */}
          <div style={{ marginTop: 12 }}>
            {STAT_ROWS.map(({ label, value, pro }, i) => (
              <div key={label} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "13px 0",
                borderTop: i > 0 ? "1px solid rgba(255,255,255,0.07)" : "none",
              }}>
                <div style={{ display: "flex", alignItems: "center" }}>
                  <span style={{
                    fontSize: 14, color: "rgba(255,255,255,0.52)", fontWeight: 400,
                  }}>{label}</span>
                  {pro && <ProBadge/>}
                </div>
                <span style={{ fontSize: 14, fontWeight: 600, color: "#fff" }}>{value}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<PlayerStats/>);
