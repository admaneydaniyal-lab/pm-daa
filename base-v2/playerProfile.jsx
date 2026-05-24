// Prematch — Player Profile
// Lewis Bilbie · Striker #9 · Ravenshead FC

// ─── Icon primitives ─────────────────────────────────────────
const Sicon = ({ children, size = 22, sw = 1.6, stroke = "currentColor", fill = "none", style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={stroke}
       strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" style={style}>
    {children}
  </svg>
);

const Ic = {
  arrowL:   (p) => <Sicon {...p}><path d="M19 12H5M12 5l-7 7 7 7"/></Sicon>,
  star:     (p) => <Sicon {...p}><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></Sicon>,
  arrowUR:  (p) => <Sicon {...p}><path d="M7 17L17 7"/><path d="M9 7h8v8"/></Sicon>,
  info:     (p) => <Sicon {...p}><circle cx="12" cy="12" r="9"/><path d="M12 17v-5M12 8h.01"/></Sicon>,
  ic_news:  (p) => <Sicon {...p}><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 8h10M7 12h10M7 16h6"/></Sicon>,
  ic_match: (p) => <Sicon {...p}><path d="M4 7h16v10H4z"/><path d="M4 11h16M4 13h16M9 7v10M15 7v10"/></Sicon>,
  ic_team:  (p) => <Sicon {...p}><path d="M3 6.5L12 3l9 3.5v3a9 9 0 01-9 9 9 9 0 01-9-9v-3z"/></Sicon>,
  ic_follow:(p) => <Sicon {...p}><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></Sicon>,
  ic_prof:  (p) => <Sicon {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0116 0"/></Sicon>,
};

const Pic = {
  arrowRight: (p) => (
    <svg width={p?.size || 14} height={p?.size || 14} viewBox="0 0 256 256" fill="currentColor" style={p?.style}>
      <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"/>
    </svg>
  ),
};

// ─── Animation hook ───────────────────────────────────────────
function useCountUp(target, duration = 1200) {
  const [val, setVal] = React.useState(0);
  React.useEffect(() => {
    let raf;
    const start = performance.now();
    const tick = (t) => {
      const p = Math.min(1, (t - start) / duration);
      setVal(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target]);
  return val;
}

// ─── HexCheck verified badge ──────────────────────────────────
function HexCheck({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 26 26" fill="none">
      <path d="M13 1 L24 7 L24 19 L13 25 L2 19 L2 7 Z" fill="#c8f135"/>
      <path d="M8.5 13 L11.5 16 L17.5 10"
            stroke="#0d0d0d" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

// ─── PRO badge ────────────────────────────────────────────────
function ProBadge() {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      background: "#6d28d9", color: "#fff",
      fontSize: 9, fontWeight: 800, letterSpacing: "0.06em",
      borderRadius: 4, padding: "2px 5px", marginLeft: 6,
    }}>PRO</span>
  );
}

// ─── Jersey SVG ───────────────────────────────────────────────
function Jersey({ number = 9 }) {
  return (
    <div style={{ position: "relative", width: 86, height: 92 }}>
      <svg width="86" height="92" viewBox="0 0 86 92" fill="none">
        {/* Body */}
        <path d="M21 22 L3 37 L15 48 L20 43 L20 84 L66 84 L66 43 L71 48 L83 37 L65 22 Q59 31 43 31 Q27 31 21 22Z"
              fill="#181818" stroke="#282828" strokeWidth="1"/>
        {/* V-collar */}
        <path d="M33 26 L43 38 L53 26" stroke="#2e2e2e" strokeWidth="1.5" fill="none" strokeLinecap="round"/>
        {/* Lime chevron accent */}
        <path d="M27 57 L43 66 L59 57"
              stroke="#c8f135" strokeWidth="2.2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
      {/* Jersey number */}
      <div style={{
        position: "absolute", top: 36, left: 0, right: 0,
        textAlign: "center",
        fontSize: 21, fontWeight: 900, color: "#fff",
        letterSpacing: "-0.02em", lineHeight: 1,
        fontFamily: "inherit",
      }}>{number}</div>
    </div>
  );
}

// ─── Compare toggle: Team | League ───────────────────────────
function CompareToggle({ value, onChange }) {
  return (
    <div style={{
      display: "inline-flex",
      background: "#111", border: "1px solid #242424",
      borderRadius: 999, padding: 3, gap: 2,
    }}>
      {["Team", "League"].map((opt) => {
        const active = value === opt.toLowerCase();
        return (
          <button key={opt} onClick={() => onChange(opt.toLowerCase())} style={{
            background: active ? "#fff" : "transparent",
            color: active ? "#0d0d0d" : "#555",
            border: "none", borderRadius: 999,
            padding: "4px 12px",
            fontSize: 11, fontWeight: 700, letterSpacing: "-0.01em",
            cursor: "pointer", fontFamily: "inherit",
            transition: "background 160ms, color 160ms",
          }}>{opt}</button>
        );
      })}
    </div>
  );
}

// ─── Vertical bar pair ────────────────────────────────────────
function VertBarPair({ playerVal, compVal, max, barsReady, compLabel = "TM", barH = 64 }) {
  const BW = 18;
  const GAP = 8;
  const pPct = barsReady ? Math.min(96, (playerVal / max) * 100) : 0;
  const cPct = barsReady ? Math.min(96, (compVal   / max) * 100) : 0;

  return (
    <div>
      {/* Bars */}
      <div style={{
        display: "flex", alignItems: "flex-end", gap: GAP,
        height: barH,
        borderBottom: "1px solid #242424",
      }}>
        <div style={{
          width: BW,
          height: `${pPct}%`,
          minHeight: pPct > 0 ? 3 : 0,
          background: "#c8f135",
          borderRadius: "3px 3px 0 0",
          transition: "height 700ms cubic-bezier(0.2,0.7,0.2,1)",
        }}/>
        <div style={{
          width: BW,
          height: `${cPct}%`,
          minHeight: cPct > 0 ? 3 : 0,
          background: "#2c2c2c",
          borderRadius: "3px 3px 0 0",
          transition: "height 700ms cubic-bezier(0.2,0.7,0.2,1) 60ms",
        }}/>
      </div>

      {/* Value labels */}
      <div style={{ display: "flex", gap: GAP, marginTop: 6 }}>
        <div style={{ width: BW, textAlign: "center" }}>
          <div style={{
            fontSize: 12, fontWeight: 800, color: "#fff",
            letterSpacing: "-0.01em", fontVariantNumeric: "tabular-nums",
          }}>{playerVal}</div>
          <div style={{
            fontSize: 7, fontWeight: 800, color: "#c8f135",
            letterSpacing: "0.1em", textTransform: "uppercase", marginTop: 1,
          }}>YOU</div>
        </div>
        <div style={{ width: BW, textAlign: "center" }}>
          <div style={{
            fontSize: 12, fontWeight: 700, color: "#3e3e3e",
            letterSpacing: "-0.01em", fontVariantNumeric: "tabular-nums",
          }}>{compVal}</div>
          <div style={{
            fontSize: 7, fontWeight: 800, color: "#3e3e3e",
            letterSpacing: "0.1em", textTransform: "uppercase", marginTop: 1,
          }}>{compLabel}</div>
        </div>
      </div>
    </div>
  );
}

// ─── Percentage row (horizontal fill) ────────────────────────
function PctRow({ value, label, rankChip, animDelay = 300 }) {
  const [ready, setReady] = React.useState(false);
  React.useEffect(() => {
    const t = setTimeout(() => setReady(true), animDelay);
    return () => clearTimeout(t);
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div style={{
          fontSize: 28, fontWeight: 900, color: "#fff",
          letterSpacing: "-0.03em", lineHeight: 1,
          fontVariantNumeric: "tabular-nums",
        }}>{value}%</div>
        {rankChip && (
          <div style={{
            fontSize: 9, fontWeight: 800, color: "#c8f135",
            letterSpacing: "0.12em", textTransform: "uppercase",
          }}>{rankChip}</div>
        )}
      </div>
      <div style={{
        fontSize: 10, fontWeight: 700, color: "#555",
        letterSpacing: "0.14em", textTransform: "uppercase", marginTop: 3,
      }}>{label}</div>
      <div style={{ marginTop: 8, height: 3, background: "#181818", borderRadius: 2, overflow: "hidden" }}>
        <div style={{
          width: ready ? `${value}%` : "0%",
          height: "100%", background: "#c8f135", borderRadius: 2,
          transition: "width 900ms cubic-bezier(0.2,0.7,0.2,1)",
        }}/>
      </div>
    </div>
  );
}

// ─── Mini sparkline ───────────────────────────────────────────
function MiniSparkline({ width = 114, height = 44 }) {
  const pts = [0.60, 0.57, 0.64, 0.60, 0.68, 0.72, 0.70, 0.78, 0.84, 0.83, 0.91, 1.0];
  const PL = 2, PR = 4, PT = 4, PB = 4;
  const cW = width - PL - PR;
  const cH = height - PT - PB;
  const step = cW / (pts.length - 1);
  const xAt = (i) => PL + i * step;
  const yAt = (v) => PT + cH * (1 - v);
  let d = `M ${xAt(0)} ${yAt(pts[0])}`;
  for (let i = 1; i < pts.length; i++) {
    const cx = (xAt(i - 1) + xAt(i)) / 2;
    d += ` C ${cx} ${yAt(pts[i-1])}, ${cx} ${yAt(pts[i])}, ${xAt(i)} ${yAt(pts[i])}`;
  }
  const dArea = d + ` L ${xAt(pts.length-1)} ${PT+cH} L ${PL} ${PT+cH} Z`;
  const lx = xAt(pts.length - 1);
  const ly = yAt(pts[pts.length - 1]);

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ display: "block" }}>
      <defs>
        <linearGradient id="prof-spark-fill" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%"   stopColor="#c8f135" stopOpacity="0.28"/>
          <stop offset="100%" stopColor="#c8f135" stopOpacity="0"/>
        </linearGradient>
      </defs>
      <path d={dArea} fill="url(#prof-spark-fill)"/>
      <path d={d} fill="none" stroke="#c8f135" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx={lx} cy={ly} r="3" fill="#c8f135"/>
    </svg>
  );
}

// ─── Bottom tab bar ───────────────────────────────────────────
function TabBar() {
  const items = [
    { key: "news",   label: "News",      Icon: Ic.ic_news,   active: false },
    { key: "match",  label: "Matches",   Icon: Ic.ic_match,  active: false },
    { key: "team",   label: "Team",      Icon: Ic.ic_team,   active: false },
    { key: "follow", label: "Following", Icon: Ic.ic_follow, active: false },
    { key: "prof",   label: "Profile",   Icon: Ic.ic_prof,   active: true  },
  ];
  return (
    <div style={{
      position: "absolute", left: 0, right: 0, bottom: 0,
      height: 68, background: "#0d0d0d",
      borderTop: "1px solid #1c1c1c",
      display: "flex", alignItems: "center", zIndex: 10,
    }}>
      {items.map(({ key, label, Icon, active }) => (
        <button key={key} style={{
          flex: 1, height: "100%",
          background: "transparent", border: 0,
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 4,
          color: active ? "#fff" : "#555",
          cursor: "pointer", fontFamily: "inherit",
        }}>
          <Icon size={22} sw={active ? 2 : 1.6}/>
          <div style={{ fontSize: 11, fontWeight: active ? 800 : 600, letterSpacing: "-0.01em" }}>{label}</div>
        </button>
      ))}
    </div>
  );
}

// ─── Data ─────────────────────────────────────────────────────
// Averages are forward/striker-position-filtered, not whole-squad
const PERF_STATS = [
  {
    key: "goals",
    label: "Goals",
    unit: "scored",
    value: 9,
    teamAvg: 2.2, leagueAvg: 1.8, max: 12,
    teamCompare:   "+6.8 vs fwds",
    leagueCompare: "T-1st · NSL",
    chip: { value: "147", label: "Mins / Goal" },
    icon: (
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <circle cx="12" cy="12" r="9"/>
        <path d="M12 3l3 4-1 5-4 0-1-5z"/>
        <path d="M15 7l5 1M9 7L4 8M14 12l3 6M10 12l-3 6"/>
      </svg>
    ),
  },
  {
    key: "assists",
    label: "Assists",
    unit: "created",
    value: 4,
    teamAvg: 1.2, leagueAvg: 0.9, max: 6,
    teamCompare:   "+2.8 vs fwds",
    leagueCompare: "#7 in league",
    chip: { value: "3×", label: "Top XI" },
    icon: (
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
        <path d="M22 4L12 14.01l-3-3"/>
      </svg>
    ),
  },
  {
    key: "games",
    label: "Games",
    unit: "played",
    value: 20,
    teamAvg: 17, leagueAvg: 15, max: 22,
    teamCompare:   "+3 vs fwds",
    leagueCompare: "Top 8% STs",
    chip: { value: "1,740", label: "Mins Played" },
    icon: (
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <rect x="3" y="4" width="18" height="16" rx="2"/>
        <path d="M3 10h18"/>
      </svg>
    ),
  },
];

const STAT_ROWS = [
  { label: "Matches Played",   value: "20",    pro: false, teamRank: 2, leagueRank: 8  },
  { label: "Mins Played",      value: "1,740", pro: true,  teamRank: 2, leagueRank: 7  },
  { label: "Starting XI",      value: "89%",   pro: false, teamRank: 2, leagueRank: 11 },
  { label: "Goals",            value: "9",     pro: false, teamRank: 1, leagueRank: 1  },
  { label: "Mins per Goal",    value: "147",   pro: true,  teamRank: 1, leagueRank: 3  },
  { label: "Assists",          value: "4",     pro: false, teamRank: 2, leagueRank: 7  },
  { label: "Shots on Target",  value: "22",    pro: true,  teamRank: 1, leagueRank: 4  },
  { label: "Conversion Rate",  value: "41%",   pro: true,  teamRank: 1, leagueRank: 2  },
  { label: "Win %",            value: "56%",   pro: false, teamRank: 4, leagueRank: 14 },
  { label: "Top XI",           value: "3",     pro: true,  teamRank: 1, leagueRank: 5  },
];

const STATS_ROWS = [
  { label: "Matches Played",  value: "18",   pro: false, teamRank: 4, leagueRank: 23 },
  { label: "Mins Played",     value: "1521", pro: true,  teamRank: 3, leagueRank: 19 },
  { label: "Starting XI",     value: "89%",  pro: false, teamRank: 2, leagueRank: 11 },
  { label: "Goals",           value: "9",    pro: false, teamRank: 1, leagueRank: 1  },
  { label: "Mins per Goal",   value: "147",  pro: true,  teamRank: 1, leagueRank: 3  },
  { label: "Assists",         value: "4",    pro: false, teamRank: 1, leagueRank: 7  },
  { label: "Clean Sheets",    value: "5",    pro: false, teamRank: 3, leagueRank: 14 },
  { label: "Clean Sheet %",   value: "28%",  pro: false, teamRank: 4, leagueRank: 16 },
  { label: "Win %",           value: "56%",  pro: false, teamRank: 6, leagueRank: 14 },
  { label: "Top XI",          value: "3",    pro: true,  teamRank: 1, leagueRank: 5  },
];

const TABS = ["Overview", "Stats", "Matches", "Career"];

// ─── Main screen ──────────────────────────────────────────────
function PlayerProfile() {
  const [activeTab,   setActiveTab]   = React.useState("Overview");
  const [scrolled,    setScrolled]    = React.useState(false);
  const [compareMode, setCompareMode] = React.useState("team");
  const [barsReady,   setBarsReady]   = React.useState(false);
  const scrollRef = React.useRef(null);

  React.useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const onScroll = () => setScrolled(el.scrollTop > 160);
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  React.useEffect(() => {
    const t = setTimeout(() => setBarsReady(true), 220);
    return () => clearTimeout(t);
  }, []);

  const animatedMV = useCountUp(24300, 1200);

  return (
    <div style={{ position: "absolute", inset: 0, background: "#0d0d0d" }}>

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
          <button style={{ background: "none", border: "none", color: "#fff", cursor: "pointer", padding: "4px 2px", display: "flex" }}>
            <Ic.arrowL size={22}/>
          </button>
          <span style={{
            fontWeight: 800, fontSize: 12, color: "#fff",
            letterSpacing: "0.06em", textTransform: "uppercase",
            opacity: scrolled ? 1 : 0,
            transition: "opacity 200ms",
          }}>Lewis Bilbie</span>
          <button style={{ background: "none", border: "none", color: "#fff", cursor: "pointer", padding: "4px 2px", display: "flex" }}>
            <Ic.star size={22}/>
          </button>
        </div>
      </div>

      {/* ── Scroll body ── */}
      <div ref={scrollRef} className="scroll-area"
           style={{ position: "absolute", inset: 0, overflowY: "auto" }}>

        {/* ── Hero card ── */}
        <div style={{ padding: "106px 16px 0" }}>
          <div style={{
            background: "#131313", border: "1px solid #242424",
            borderRadius: 16, padding: "16px",
            display: "flex", alignItems: "flex-start", gap: 12,
          }}>
            {/* Name block */}
            <div style={{ flex: 1, paddingTop: 2 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{
                  fontSize: 22, fontWeight: 900, color: "#fff",
                  letterSpacing: "-0.02em", lineHeight: 1.05,
                  textTransform: "uppercase",
                }}>LEWIS<br/>BILBIE</div>
                <HexCheck size={20}/>
              </div>
              <div style={{ display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" }}>
                <span style={{
                  background: "#c8f135", color: "#0d0d0d",
                  fontSize: 10, fontWeight: 800, letterSpacing: "0.1em", textTransform: "uppercase",
                  borderRadius: 6, padding: "4px 9px",
                }}>Striker</span>
                <span style={{
                  background: "transparent", border: "1px solid #272727", color: "#666",
                  fontSize: 10, fontWeight: 700, letterSpacing: "0.05em",
                  borderRadius: 6, padding: "4px 9px",
                  display: "inline-flex", alignItems: "center", gap: 4,
                }}>Ravenshead FC <Ic.arrowUR size={10} sw={2}/></span>
              </div>
            </div>
            {/* Number */}
            <div style={{
              fontSize: 64, fontWeight: 900, color: "#fff",
              letterSpacing: "-0.04em", lineHeight: 1,
              fontVariantNumeric: "tabular-nums",
              paddingTop: 4, color: "#aaaaaa",
            }}>#9</div>
          </div>
        </div>

        {/* ── Player Comparison ── */}
        <div style={{ padding: "10px 16px 0" }}>
          <button style={{
            width: "100%",
            background: "#131313", border: "1px solid #242424",
            borderRadius: 12, padding: "11px 16px",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
            cursor: "pointer", fontFamily: "inherit",
          }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#666"
                 strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 3h5v5"/><path d="M21 3l-7 7"/>
              <path d="M8 21H3v-5"/><path d="M3 21l7-7"/>
            </svg>
            <span style={{ fontSize: 13, fontWeight: 600, color: "#666", letterSpacing: "-0.01em" }}>Player Comparison</span>
          </button>
        </div>

        {/* ── Quick stats 2×2 ── */}
        <div style={{ padding: "10px 16px 0" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
            {[
              { label: "Market Value",  value: `£${Math.round(animatedMV).toLocaleString("en-GB")}` },
              { label: "Points",        value: "1,138" },
              { label: "Followers",     value: "47"    },
              { label: "Profile Views", value: "203"   },
            ].map(({ label, value }) => (
              <div key={label} style={{
                background: "#131313", border: "1px solid #222",
                borderRadius: 10, padding: "11px 14px",
                display: "flex", justifyContent: "space-between", alignItems: "center",
              }}>
                <div style={{ fontSize: 11, fontWeight: 500, color: "#555" }}>{label}</div>
                <div style={{
                  fontSize: 13, fontWeight: 800, color: "#fff",
                  letterSpacing: "-0.01em", fontVariantNumeric: "tabular-nums",
                }}>{value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Tabs ── */}
        <div style={{
          display: "flex",
          borderBottom: "1px solid #1c1c1c",
          paddingLeft: 4, marginTop: 14,
          position: "sticky", top: 90, zIndex: 10,
          background: "#0d0d0d",
        }}>
          {TABS.map((tab) => {
            const active = tab === activeTab;
            return (
              <button key={tab} onClick={() => setActiveTab(tab)} style={{
                background: "none", border: "none", cursor: "pointer",
                padding: "12px 12px 11px",
                fontSize: 12, fontWeight: active ? 700 : 400,
                color: active ? "#fff" : "rgba(255,255,255,0.35)",
                letterSpacing: "-0.01em",
                borderBottom: `2px solid ${active ? "#fff" : "transparent"}`,
                marginBottom: -1,
                transition: "color 180ms",
                fontFamily: "inherit", whiteSpace: "nowrap",
              }}>{tab}</button>
            );
          })}
        </div>

        {/* ── Overview tab ── */}
        {activeTab === "Overview" && (
          <div style={{ paddingBottom: 100 }}>

            {/* Headline card */}
            <div style={{ padding: "14px 16px 0" }}>
              <div style={{
                background: "#0f0f0f",
                border: "1px solid #1e1e1e",
                borderLeft: "3px solid #c8f135",
                borderRadius: 10,
                padding: "11px 14px",
              }}>
                <div style={{
                  fontSize: 10, fontWeight: 800, color: "#c8f135",
                  letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 5,
                }}>2025/26 · NSL Division One</div>
                <div style={{
                  fontSize: 14, fontWeight: 400, color: "#fff", lineHeight: 1.5,
                }}>Joint top scorer in the league. Starting every game available this season.</div>
              </div>
            </div>

            {/* ── Market Value ── */}
            <div style={{ marginTop: 22 }}>
              <div style={{
                fontSize: 11, fontWeight: 800, color: "#fff",
                letterSpacing: "0.14em", textTransform: "uppercase",
                padding: "0 16px", marginBottom: 10,
              }}>Market Value</div>

              <div style={{ padding: "0 16px" }}>
                <div style={{
                  background: "#131313", border: "1px solid #242424",
                  borderRadius: 16, padding: "16px",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <div style={{
                        fontSize: 26, fontWeight: 900, color: "#fff",
                        letterSpacing: "-0.03em", lineHeight: 1,
                        fontVariantNumeric: "tabular-nums",
                      }}>£{Math.round(animatedMV).toLocaleString("en-GB")}</div>
                      <div style={{ marginTop: 5, fontSize: 12, fontWeight: 700, color: "#c8f135" }}>
                        ↗ +12.4%{" "}
                        <span style={{ color: "#555", fontWeight: 500 }}>this month</span>
                      </div>
                    </div>
                    <MiniSparkline width={114} height={44}/>
                  </div>

                  <div style={{
                    marginTop: 14, paddingTop: 12,
                    borderTop: "1px solid #1a1a1a",
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                  }}>
                    <div style={{
                      display: "inline-flex", alignItems: "center", gap: 6,
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid #1e1e1e", borderRadius: 999,
                      padding: "4px 10px 4px 8px",
                    }}>
                      <div style={{ width: 5, height: 5, borderRadius: 99, background: "#c8f135" }}/>
                      <span style={{
                        fontSize: 9, fontWeight: 700, color: "#555",
                        letterSpacing: "0.14em", textTransform: "uppercase",
                      }}>Next update</span>
                      <span style={{ fontSize: 11, fontWeight: 800, color: "#fff" }}>18:03:23</span>
                    </div>
                    <button style={{
                      background: "none", border: "none", cursor: "pointer",
                      fontFamily: "inherit",
                      display: "inline-flex", alignItems: "center", gap: 4,
                      fontSize: 12, fontWeight: 700, color: "#c8f135",
                    }}>Details <Pic.arrowRight size={11}/></button>
                  </div>

                  <div style={{
                    marginTop: 12, fontSize: 13, fontWeight: 400, color: "#fff", lineHeight: 1.45,
                  }}>
                    Up 4 weeks in a row.{" "}
                    <span style={{ fontWeight: 700 }}>2nd most valuable</span> striker on your squad.
                  </div>
                </div>
              </div>
            </div>

            {/* ── Performance section ── */}
            <div style={{ marginTop: 22 }}>
              {/* Section header + toggle */}
              <div style={{
                display: "flex", alignItems: "flex-start",
                justifyContent: "space-between",
                padding: "0 16px", marginBottom: 10, gap: 12,
              }}>
                <div>
                  <div style={{
                    fontSize: 11, fontWeight: 800, color: "#fff",
                    letterSpacing: "0.14em", textTransform: "uppercase",
                  }}>Personal Season · Performance</div>
                  <div style={{
                    fontSize: 10, fontWeight: 500, color: "#555", marginTop: 3,
                  }}>You vs your {compareMode === "team" ? "squad" : "league"}.</div>
                </div>
                <CompareToggle value={compareMode} onChange={setCompareMode}/>
              </div>

              <div style={{ padding: "0 16px" }}>
                <div style={{
                  background: "#131313", border: "1px solid #242424",
                  borderRadius: 16, overflow: "hidden",
                }}>
                  {/* Status row */}
                  <div style={{
                    padding: "9px 16px",
                    borderBottom: "1px solid #1c1c1c",
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <div style={{ width: 5, height: 5, borderRadius: 99, background: "#c8f135" }}/>
                      <span style={{
                        fontSize: 10, fontWeight: 600, color: "#4a4a4a",
                        letterSpacing: "0.08em",
                      }}>STATS · updated 3h ago</span>
                    </div>
                    <span style={{ fontSize: 10, fontWeight: 600, color: "#4a4a4a" }}>WK 12 / 38</span>
                  </div>

                  {/* 3-column vertical bar grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr" }}>
                    {PERF_STATS.map((stat, i) => {
                      const compVal      = compareMode === "team" ? stat.teamAvg   : stat.leagueAvg;
                      const compareText  = compareMode === "team" ? stat.teamCompare : stat.leagueCompare;
                      const compLabel    = compareMode === "team" ? "TM" : "LG";
                      return (
                        <div key={stat.key} style={{
                          padding: "16px 14px 14px",
                          borderRight: i < 2 ? "1px solid #1c1c1c" : "none",
                        }}>
                          {/* Label */}
                          <div style={{
                            fontSize: 9, fontWeight: 800, color: "#888",
                            letterSpacing: "0.14em", textTransform: "uppercase",
                            marginBottom: 8,
                          }}>
                            {stat.label}
                          </div>

                          {/* Big number */}
                          <div style={{
                            fontSize: 30, fontWeight: 900, color: "#fff",
                            letterSpacing: "-0.03em", lineHeight: 1,
                            fontVariantNumeric: "tabular-nums",
                          }}>{stat.value}</div>
                          <div style={{
                            fontSize: 10, fontWeight: 400, color: "#4a4a4a", marginTop: 3,
                          }}>{stat.unit}</div>

                          {/* Vertical bars */}
                          <div style={{ marginTop: 12 }}>
                            <VertBarPair
                              playerVal={stat.value}
                              compVal={compVal}
                              max={stat.max}
                              barsReady={barsReady}
                              compLabel={compLabel}
                            />
                          </div>

                          {/* Compare text */}
                          <div style={{
                            marginTop: 8,
                            fontSize: 10, fontWeight: 600, color: "#c8f135",
                            letterSpacing: "-0.01em", lineHeight: 1.3,
                          }}>{compareText}</div>

                          {/* Column chip */}
                          <div style={{
                            marginTop: 10,
                            background: "#0d0d0d", border: "1px solid #1c1c1c",
                            borderRadius: 7, padding: "6px 8px", textAlign: "center",
                          }}>
                            <div style={{
                              fontSize: 14, fontWeight: 900, color: "#fff",
                              letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums",
                            }}>{stat.chip.value}</div>
                            <div style={{
                              fontSize: 8, fontWeight: 700, color: "#4a4a4a",
                              letterSpacing: "0.1em", textTransform: "uppercase", marginTop: 2,
                            }}>{stat.chip.label}</div>
                          </div>

                        </div>
                      );
                    })}
                  </div>

                  {/* View all rankings — single outline button */}
                  <div style={{
                    padding: "12px 16px 14px",
                    borderTop: "1px solid #1c1c1c",
                    display: "flex", justifyContent: "center",
                  }}>
                    <button style={{
                      background: "transparent", color: "#c8f135",
                      border: "1px solid #c8f135", borderRadius: 999,
                      padding: "6px 18px",
                      fontFamily: "inherit", fontWeight: 700, fontSize: 12,
                      letterSpacing: "-0.01em", cursor: "pointer",
                      whiteSpace: "nowrap",
                    }}>View all rankings</button>
                  </div>
                </div>
              </div>
            </div>

            {/* ── Percentages section ── */}
            <div style={{ marginTop: 22 }}>
              <div style={{ padding: "0 16px", marginBottom: 10 }}>
                <div style={{
                  fontSize: 11, fontWeight: 800, color: "#fff",
                  letterSpacing: "0.14em", textTransform: "uppercase",
                }}>Personal Season · Percentages</div>
              </div>

              <div style={{ padding: "0 16px" }}>
                <div style={{
                  background: "#131313", border: "1px solid #242424",
                  borderRadius: 16, padding: "16px 16px 18px",
                }}>
                  <div style={{
                    fontSize: 10, fontWeight: 700, color: "#3e3e3e",
                    letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 18,
                  }}>Season 2025/26</div>

                  {[
                    { value: 89, label: "Starting XI",  rankChip: "#2 SQUAD",   delay: 300 },
                    { value: 56, label: "Win %",         rankChip: null,          delay: 420 },
                    { value: 45, label: "Goalscorer",    rankChip: "#1 SQUAD ↑", delay: 540 },
                  ].map(({ value, label, rankChip, delay }, i) => (
                    <div key={label} style={{
                      marginTop: i === 0 ? 0 : 18,
                      paddingTop: i === 0 ? 0 : 18,
                      borderTop: i === 0 ? "none" : "1px solid #1a1a1a",
                    }}>
                      <PctRow value={value} label={label} rankChip={rankChip} animDelay={delay}/>
                    </div>
                  ))}

                  {/* CTA */}
                  <div style={{
                    marginTop: 20, paddingTop: 14,
                    borderTop: "1px solid #1a1a1a",
                    display: "flex", alignItems: "center", justifyContent: "center", gap: 5,
                  }}>
                    <Ic.info size={13} stroke="#555" sw={1.8}/>
                    <button style={{
                      background: "none", border: "none", cursor: "pointer",
                      fontFamily: "inherit", display: "flex", alignItems: "center", gap: 4,
                      fontSize: 12, fontWeight: 600, color: "#555",
                    }}>
                      Learn & Correct your Statistics
                      <Pic.arrowRight size={11} style={{ color: "#555" }}/>
                    </button>
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}

        {/* ── Stats tab ── */}
        {activeTab === "Stats" && (
          <div style={{ paddingBottom: 100 }}>

            {/* Season Performance card */}
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
                {[{ v: "18", l: "Games" }, { v: "9", l: "Goals" }, { v: "4", l: "Assists" }].map(({ v, l }) => (
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

            {/* Statistical Breakdown card */}
            <div style={{
              margin: "0 14px 40px",
              background: "rgba(255,255,255,0.05)",
              borderRadius: 16, padding: "18px 20px 8px",
            }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", letterSpacing: "-0.01em" }}>
                Statistical Breakdown
              </div>

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

              <div style={{ marginTop: 20, display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>All competitions</div>
                  <div style={{ fontSize: 12, color: "rgba(255,255,255,0.42)", marginTop: 3, fontWeight: 500 }}>
                    2025/2026
                  </div>
                </div>
                <div style={{ display: "flex", paddingBottom: 2 }}>
                  <div style={{ width: 46 }}/>
                  <div style={{
                    width: 46, textAlign: "center",
                    fontSize: 10, fontWeight: 700, color: "rgba(255,255,255,0.35)",
                    letterSpacing: "0.02em", lineHeight: 1.3,
                  }}>Team<br/>Rank</div>
                  <div style={{
                    width: 46, textAlign: "center",
                    fontSize: 10, fontWeight: 700, color: "rgba(255,255,255,0.35)",
                    letterSpacing: "0.02em", lineHeight: 1.3,
                  }}>League<br/>Rank</div>
                </div>
              </div>

              <div style={{ position: "relative", marginTop: 8 }}>
                <div style={{
                  position: "absolute", top: 0, bottom: 0,
                  right: 92, width: 1,
                  background: "rgba(255,255,255,0.1)",
                  pointerEvents: "none",
                }}/>

                {STATS_ROWS.map(({ label, value, pro, teamRank, leagueRank }, i) => (
                  <div key={label} style={{
                    display: "flex", alignItems: "center",
                    padding: "12px 0",
                    borderTop: i > 0 ? "1px solid rgba(255,255,255,0.07)" : "none",
                  }}>
                    <div style={{ flex: 1, display: "flex", alignItems: "center", minWidth: 0 }}>
                      <span style={{ fontSize: 13, color: "rgba(255,255,255,0.52)", fontWeight: 400 }}>{label}</span>
                      {pro && <ProBadge/>}
                    </div>
                    <span style={{
                      fontSize: 14, fontWeight: 700, color: "#fff",
                      width: 46, textAlign: "right", paddingRight: 14,
                      fontVariantNumeric: "tabular-nums",
                    }}>{value}</span>
                    <span style={{
                      width: 46, textAlign: "center",
                      fontSize: 13, fontVariantNumeric: "tabular-nums",
                      fontWeight: teamRank === 1 ? 800 : 500,
                      color: teamRank === 1 ? "#c8f135" : "rgba(255,255,255,0.3)",
                    }}>{teamRank}</span>
                    <span style={{
                      width: 46, textAlign: "center",
                      fontSize: 13, fontVariantNumeric: "tabular-nums",
                      fontWeight: leagueRank === 1 ? 800 : leagueRank <= 3 ? 700 : 500,
                      color: leagueRank === 1 ? "#c8f135" : leagueRank <= 3 ? "#fff" : "rgba(255,255,255,0.3)",
                    }}>{leagueRank}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* ── Other tabs ── */}
        {activeTab !== "Overview" && activeTab !== "Stats" && (
          <div style={{
            padding: "60px 16px", textAlign: "center",
            color: "#3e3e3e", fontSize: 14, fontWeight: 500,
          }}>
            {activeTab} coming soon
          </div>
        )}

      </div>

      <TabBar/>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<PlayerProfile/>);
