// Prematch — Base (home) screen v2
// New element: horizontal 4-card carousel hero between greeting and quick access.
// Below carousel: quick access row, league table, newsfeed (unchanged in spirit).

// ─────────────────────────────────────────────────────────────
// Icons (inline SVG, Lucide-style, 1.6px stroke)
// ─────────────────────────────────────────────────────────────
const Sicon = ({ children, size = 22, sw = 1.6, stroke = "currentColor", fill = "none", style }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={stroke}
       strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" style={style}>
    {children}
  </svg>
);
const Ic = {
  search:   (p) => <Sicon {...p}><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></Sicon>,
  bell:     (p) => <Sicon {...p}><path d="M18 16H6a2 2 0 01-2-2l1.5-1.5V9a6.5 6.5 0 0113 0v3.5L20 14a2 2 0 01-2 2z"/><path d="M10 19a2 2 0 004 0"/></Sicon>,
  arrowUR:  (p) => <Sicon {...p}><path d="M7 17L17 7"/><path d="M9 7h8v8"/></Sicon>,
  arrowR:   (p) => <Sicon {...p}><path d="M5 12h14"/><path d="M13 5l7 7-7 7"/></Sicon>,
  bookmark: (p) => <Sicon {...p}><path d="M7 4h10v17l-5-3.5L7 21V4z"/></Sicon>,
  table:    (p) => <Sicon {...p}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M3 16h18M9 4v16"/></Sicon>,
  refer:    (p) => <Sicon {...p}><circle cx="9" cy="9" r="3.5"/><path d="M3 20a6 6 0 0112 0"/><path d="M17 11v6M14 14h6"/></Sicon>,
  team:     (p) => <Sicon {...p}><circle cx="8" cy="9" r="3"/><circle cx="16" cy="9" r="3"/><path d="M2 19a6 6 0 0112 0"/><path d="M14 13a6 6 0 018 6"/></Sicon>,
  trophy:   (p) => <Sicon {...p}><path d="M8 4h8v5a4 4 0 01-8 0V4z"/><path d="M5 5H3v2a3 3 0 003 3M19 5h2v2a3 3 0 01-3 3"/><path d="M10 14v4h4v-4M8 21h8"/></Sicon>,
  share:    (p) => <Sicon {...p}><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8 11l8-4"/><path d="M8 13l8 4"/></Sicon>,
  thumb:    (p) => <Sicon {...p}><path d="M7 22V11l5-8a2.5 2.5 0 012.5 4.5L13 11h5.5a2.5 2.5 0 012.4 3l-1.5 6.5a2.5 2.5 0 01-2.4 1.5H7z"/></Sicon>,
  cursor:   (p) => <Sicon {...p}><path d="M4 3l6 17 2.5-7L19 11z"/></Sicon>,
  minus:    (p) => <Sicon {...p}><circle cx="12" cy="12" r="8"/><path d="M8 12h8"/></Sicon>,
  // bottom tab
  ic_base:  (p) => <Sicon {...p}><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/></Sicon>,
  ic_match: (p) => <Sicon {...p}><path d="M4 7h16v10H4z"/><path d="M4 11h16M4 13h16M9 7v10M15 7v10"/></Sicon>,
  ic_team:  (p) => <Sicon {...p}><path d="M3 6.5L12 3l9 3.5v3a9 9 0 01-9 9 9 9 0 01-9-9v-3z"/></Sicon>,
  ic_league:(p) => <Sicon {...p}><path d="M8 4h8v5a4 4 0 01-8 0V4z"/><path d="M5 5H3v2a3 3 0 003 3M19 5h2v2a3 3 0 01-3 3"/><path d="M10 14v4h4v-4M8 21h8"/></Sicon>,
  ic_prof:  (p) => <Sicon {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0116 0"/></Sicon>,
  ball:     (p) => <Sicon {...p} sw={1.4}><circle cx="12" cy="12" r="9"/><path d="M12 3l3 4-1 5-4 0-1-5z"/><path d="M15 7l5 1M9 7L4 8M14 12l3 6M10 12l-3 6"/></Sicon>,
  shield:   (p) => <Sicon {...p}><path d="M12 3l8 3v6c0 4.5-3.4 8.4-8 9-4.6-.6-8-4.5-8-9V6l8-3z"/></Sicon>,
  money:    (p) => <Sicon {...p}><path d="M15 6h-4a3 3 0 000 6h2a3 3 0 010 6H8"/><path d="M12 4v3M12 17v3"/></Sicon>,
};

// ─────────────────────────────────────────────────────────────
// Hex logo
// ─────────────────────────────────────────────────────────────
function HexLogo({ size = 38 }) {
  return (
    <div style={{
      width: size, height: size, position: "relative",
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <svg width={size} height={size} viewBox="0 0 40 40" style={{ position: "absolute", inset: 0 }}>
        <path d="M20 1 L37.3 11 L37.3 29 L20 39 L2.7 29 L2.7 11 Z"
              fill="#000" stroke="#fff" strokeWidth="1.8"/>
      </svg>
      <span style={{
        position: "relative", color: "#fff",
        fontWeight: 900, fontSize: size * 0.5,
        letterSpacing: "-0.04em",
      }}>P</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Top app bar — logo, Get PRO pill, search, bell
// ─────────────────────────────────────────────────────────────
function TopBar() {
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "8px 16px 0",
      height: 56,
    }}>
      <HexLogo size={38}/>
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <button style={{
          background: "#a78bfa", color: "#0d0d0d",
          border: 0, borderRadius: 8, padding: "7px 12px",
          fontFamily: "inherit", fontWeight: 800, fontSize: 13,
          letterSpacing: "-0.01em", cursor: "pointer",
          marginRight: 6,
        }}>Get PRO</button>
        <button style={{
          background: "transparent", border: 0, color: "#fff",
          padding: 8, cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}><Ic.search size={22}/></button>
        <button style={{
          background: "transparent", border: 0, color: "#fff",
          padding: 8, cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
        }} onClick={() => window.postMessage({ type: '__activate_edit_mode' }, '*')}>
          <Ic.bell size={22}/>
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Greeting
// ─────────────────────────────────────────────────────────────
function Greeting({ name }) {
  return (
    <div style={{
      padding: "20px 16px 16px",
    }}>
      <div style={{
        fontSize: 24, fontWeight: 900, color: "var(--fg)",
        letterSpacing: "-0.02em", textTransform: "uppercase",
      }}>Hi, {name}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Carousel card shell
// ─────────────────────────────────────────────────────────────
function CardShell({ header, subheader, narrativeIcon, narrative, cta, pulse, children }) {
  return (
    <div className={pulse ? "pm-card-pulse" : undefined} style={{
      position: "relative",
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: 18,
      isolation: "isolate",
      padding: "14px 18px 14px",
      height: "100%",
      boxSizing: "border-box",
      display: "flex", flexDirection: "column",
      cursor: "pointer",
    }}>
      {/* Top row: header only */}
      <div style={{ minWidth: 0 }}>
        <div style={{
          fontSize: 11, fontWeight: 800, color: "var(--fg)",
          letterSpacing: "0.18em", textTransform: "uppercase",
          lineHeight: 1.2,
        }}>{header}</div>
        {subheader && (
          <div style={{
            marginTop: 3,
            fontSize: 10, fontWeight: 600, color: "var(--fg-muted)",
            letterSpacing: "0.16em", textTransform: "uppercase",
            lineHeight: 1.2,
          }}>{subheader}</div>
        )}
      </div>

      {children}

      {/* Narrative sits tight under content; CTA gets pushed to the bottom */}
      {narrative && (
        <div style={{
          marginTop: 22,
          display: "flex", alignItems: "center", gap: 10,
          paddingRight: 4,
        }}>
          {narrativeIcon && (
            <div style={{
              flex: "0 0 auto",
              color: "var(--accent)",
            }}>{narrativeIcon}</div>
          )}
          <div style={{
            fontSize: 13, fontWeight: 400, color: "var(--fg)",
            lineHeight: 1.4,
          }}>{narrative}</div>
        </div>
      )}
      <div style={{ flex: 1 }}/>
      {cta && (
        <div style={{
          marginTop: 10,
          display: "inline-flex", alignItems: "center", gap: 6,
          fontSize: 12, fontWeight: 700,
          color: "var(--accent)",
          letterSpacing: "-0.01em",
          lineHeight: 1.2,
          alignSelf: "flex-start",
        }}>
          <span>{cta}</span>
          <Pic.arrowRight size={12}/>
        </div>
      )}
    </div>
  );
}

// Hero number with lime underline accent (fills in on mount)
function LimeHero({ value, fontSize = 88, underlineWidth = "70%" }) {
  const [filled, setFilled] = React.useState(false);
  React.useEffect(() => {
    const t = setTimeout(() => setFilled(true), 80);
    return () => clearTimeout(t);
  }, []);
  return (
    <div style={{ display: "inline-block", position: "relative", paddingBottom: 6 }}>
      <div style={{
        fontWeight: 900, fontSize, color: "var(--fg)",
        letterSpacing: "-0.04em", lineHeight: 0.9,
        fontVariantNumeric: "tabular-nums",
      }}>{value}</div>
      <div style={{
        position: "absolute", left: 0, bottom: -2,
        width: filled ? underlineWidth : "0%",
        height: 6,
        background: "var(--accent)",
        borderRadius: 2,
        transition: "width 760ms cubic-bezier(0.2, 0.7, 0.2, 1)",
        transitionDelay: "120ms",
      }}/>
    </div>
  );
}

// Count-up animation hook (ease-out cubic)
function useCountUp(target, duration = 1400, deps = []) {
  const [val, setVal] = React.useState(0);
  React.useEffect(() => {
    let raf;
    const start = performance.now();
    const tick = (t) => {
      const p = Math.min(1, (t - start) / duration);
      const ease = 1 - Math.pow(1 - p, 3);
      setVal(target * ease);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  // eslint-disable-next-line
  }, [target, duration, ...deps]);
  return val;
}

// Phosphor-style filled brand icons (passed in via narrativeIcon slot)
const Pic = {
  ball:   (p) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={p?.size || 16} height={p?.size || 16}
         viewBox="0 0 256 256" fill="currentColor" style={p?.style}>
      <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm76.52,147.42H170.9l-9.26-12.76,12.63-36.78,15-4.89,26.24,20.13A87.38,87.38,0,0,1,204.52,171.42Zm-164-34.3L66.71,117l15,4.89,12.63,36.78L85.1,171.42H51.48A87.38,87.38,0,0,1,40.47,137.12Zm10-50.64,5.51,18.6L40.71,116.77A87.33,87.33,0,0,1,50.43,86.48ZM109,152,97.54,118.65,128,97.71l30.46,20.94L147,152Zm91.07-46.92,5.51-18.6a87.33,87.33,0,0,1,9.72,30.29Zm-6.2-35.38-9.51,32.08-15.07,4.89L136,83.79V68.21l29.09-20A88.58,88.58,0,0,1,193.86,69.7ZM146.07,41.87,128,54.29,109.93,41.87a88.24,88.24,0,0,1,36.14,0ZM90.91,48.21l29.09,20V83.79L86.72,106.67l-15.07-4.89L62.14,69.7A88.58,88.58,0,0,1,90.91,48.21ZM63.15,187.42H83.52l7.17,20.27A88.4,88.4,0,0,1,63.15,187.42ZM110,214.13,98.12,180.71,107.35,168h41.3l9.23,12.71-11.83,33.42a88,88,0,0,1-36.1,0Zm55.36-6.44,7.17-20.27h20.37A88.4,88.4,0,0,1,165.31,207.69Z"/>
    </svg>
  ),
  shield: (p) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={p?.size || 16} height={p?.size || 16}
         viewBox="0 0 256 256" fill="currentColor" style={p?.style}>
      <path d="M80.57,117A8,8,0,0,1,91,112.57l29,11.61V96a8,8,0,0,1,16,0v28.18l29-11.61A8,8,0,1,1,171,127.43l-30.31,12.12L158.4,163.2a8,8,0,1,1-12.8,9.6L128,149.33,110.4,172.8a8,8,0,1,1-12.8-9.6l17.74-23.65L85,127.43A8,8,0,0,1,80.57,117ZM224,56v56c0,52.72-25.52,84.67-46.93,102.19-23.06,18.86-46,25.27-47,25.53a8,8,0,0,1-4.2,0c-1-.26-23.91-6.67-47-25.53C57.52,196.67,32,164.72,32,112V56A16,16,0,0,1,48,40H208A16,16,0,0,1,224,56Zm-16,0L48,56l0,56c0,37.3,13.82,67.51,41.07,89.81A128.25,128.25,0,0,0,128,223.62a129.3,129.3,0,0,0,39.41-22.2C194.34,179.16,208,149.07,208,112Z"/>
    </svg>
  ),
  trophy: (p) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={p?.size || 16} height={p?.size || 16}
         viewBox="0 0 256 256" fill="currentColor" style={p?.style}>
      <path d="M232,64H208V48a8,8,0,0,0-8-8H56a8,8,0,0,0-8,8V64H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-29,64.64-64,64.9a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"/>
    </svg>
  ),
  dollar: (p) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={p?.size || 16} height={p?.size || 16}
         viewBox="0 0 256 256" fill="currentColor" style={p?.style}>
      <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm40-68a28,28,0,0,1-28,28h-4v8a8,8,0,0,1-16,0v-8H104a8,8,0,0,1,0-16h36a12,12,0,0,0,0-24H116a28,28,0,0,1,0-56h4V72a8,8,0,0,1,16,0v8h16a8,8,0,0,1,0,16H116a12,12,0,0,0,0,24h24A28,28,0,0,1,168,148Z"/>
    </svg>
  ),
  arrowRight: (p) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={p?.size || 14} height={p?.size || 14}
         viewBox="0 0 256 256" fill="currentColor" style={p?.style}>
      <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"/>
    </svg>
  ),
  sub: (p) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={p?.size || 16} height={p?.size || 16}
         viewBox="0 0 256 256" fill="currentColor" style={p?.style}>
      <path d="M213.66,181.66l-32,32a8,8,0,0,1-11.32-11.32L188.69,184H48a8,8,0,0,1,0-16H188.69l-18.35-18.34a8,8,0,0,1,11.32-11.32l32,32A8,8,0,0,1,213.66,181.66Zm-139.32-64a8,8,0,0,0,11.32-11.32L67.31,88H208a8,8,0,0,0,0-16H67.31L85.66,53.66A8,8,0,0,0,74.34,42.34l-32,32a8,8,0,0,0,0,11.32Z"/>
    </svg>
  ),
};

// Shared result colors — used by both Card 1 result text and Card 2 form pills
const WIN_GREEN  = "#22c55e";
const LOSS_RED   = "#ef4444";
const DRAW_AMBER = "#f5b53b";

// ─────────────────────────────────────────────────────────────
// CARD 1 — Post-Match Briefing (WON / LOST variants)
// ─────────────────────────────────────────────────────────────
// ─────────────────────────────────────────────────────────────
// Confetti — football-themed celebration (tiny soccer balls + lime/white/green ribbons)
// Subtle, classy: ~18 pieces, gentle fall + slow rotation, loops infinitely.
// ─────────────────────────────────────────────────────────────
function MiniBall({ size = 9 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20">
      <circle cx="10" cy="10" r="9" fill="#ffffff"/>
      <polygon points="10,5 13.5,7.5 12,11.5 8,11.5 6.5,7.5" fill="#1a1a1a"/>
      <path d="M5 9 L3 10 M15 9 L17 10 M8 13 L7 16 M12 13 L13 16" stroke="#1a1a1a" strokeWidth="0.8" fill="none"/>
    </svg>
  );
}

function Confetti({ playKey }) {
  // Recompute particle params whenever playKey changes (variant switch / remount)
  const pieces = React.useMemo(() => {
    const N = 22;
    const colors = ["#c8f135", "#ffffff", "#22c55e", "#c8f135", "#c8f135"]; // lime-heavy mix
    return Array.from({ length: N }, () => {
      const r = Math.random;
      const isBall = r() < 0.28;
      return {
        isBall,
        color: colors[Math.floor(r() * colors.length)],
        left: r() * 100,                            // % across card
        sway: (r() - 0.5) * 64,                     // horizontal drift in px
        size: isBall ? 8 + Math.round(r() * 3) : 3 + Math.round(r() * 4),
        length: 4 + Math.round(r() * 8),            // ribbon length
        rotStart: Math.round(r() * 360),
        rotEnd: Math.round(360 + r() * 540) * (r() < 0.5 ? -1 : 1),
        delay: Math.round(r() * 250),               // tight stagger; all in by ~0.25s
        duration: 2600 + Math.round(r() * 2200),    // original slow fall speed
        opacity: 0.55 + r() * 0.4,
      };
    });
  }, [playKey]);

  return (
    <div className="pm-confetti-layer" aria-hidden="true">
      {pieces.map((p, i) => (
        <span key={`${playKey}-${i}`} className="pm-confetti-piece"
          style={{
            left: `${p.left}%`,
            width: p.isBall ? p.size : p.size,
            height: p.isBall ? p.size : p.length,
            background: p.isBall ? "transparent" : p.color,
            borderRadius: p.isBall ? 0 : 2,
            opacity: p.opacity,
            animationDelay: `${p.delay}ms`,
            animationDuration: `${p.duration}ms`,
            ["--sway"]: `${p.sway}px`,
            ["--rot-start"]: `${p.rotStart}deg`,
            ["--rot-end"]: `${p.rotEnd}deg`,
          }}>
          {p.isBall && <MiniBall size={p.size}/>}
        </span>
      ))}
    </div>
  );
}

function CardBriefing({ variant = "won" }) {
  const isLost = variant === "lost";

  // Celebration sequence: confetti for ~1.5s, then a 1s glow pulse
  const [showConfetti, setShowConfetti] = React.useState(variant === "won");
  const [pulse, setPulse]               = React.useState(false);
  React.useEffect(() => {
    if (variant !== "won") {
      setShowConfetti(false);
      setPulse(false);
      return;
    }
    setShowConfetti(true);
    setPulse(false);
    const t1 = setTimeout(() => {
      setShowConfetti(false);
      setPulse(true);
    }, 2500);
    const t2 = setTimeout(() => setPulse(false), 2500 + 1000);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [variant]);

  const data = isLost ? {
    sub:       "vs Mansfield · Sat 11 May",
    result:    "LOST 2\u20134",
    resultClr: LOSS_RED,
    role:      "Subbed in",
    roleMins:  <span style={{ display: "inline-flex", alignItems: "center", gap: 3 }}>40 minutes (50' <Pic.sub size={10}/>)</span>,
    heroValue: "2",
    heroLabel: "goal contributions",
    narrative: "1 goal, 1 assist off the bench. Your most impactful sub appearance of the season.",
  } : {
    sub:       "vs Riverside · Sat 18 May",
    result:    "WON 3\u20131",
    resultClr: WIN_GREEN,
    role:      "Starting XI",
    roleMins:  "90 minutes",
    heroValue: "3",
    heroLabel: "goals",
    narrative: "Your first hat trick of the season. That's 9 goals for the year, joint top in your league.",
  };

  return (
    <CardShell
      header="Post-Match Briefing"
      subheader={data.sub}
      narrativeIcon={<Pic.ball size={20}/>}
      narrative={data.narrative}
      cta="View match details"
      pulse={pulse}
    >
      {showConfetti && <Confetti playKey={variant}/>}
      {/* Match context row */}
      <div style={{
        marginTop: 10,
        display: "flex", alignItems: "center", gap: 12,
      }}>
        <div style={{
          fontWeight: 900, fontSize: 22, color: data.resultClr,
          letterSpacing: "-0.02em",
          fontVariantNumeric: "tabular-nums",
        }}>{data.result}</div>
        <div style={{
          marginLeft: "auto",
          textAlign: "right",
          fontSize: 10, fontWeight: 700, color: "var(--fg-muted)",
          letterSpacing: "0.14em", textTransform: "uppercase",
          lineHeight: 1.3,
        }}>{data.role}<br/>{data.roleMins}</div>
      </div>

      <div style={{
        marginTop: 10, marginBottom: 8,
        height: 1, background: "var(--border)",
      }}/>

      {/* Hero number */}
      <div style={{ display: "flex", alignItems: "flex-end", gap: 12 }}>
        <LimeHero value={data.heroValue} fontSize={72} underlineWidth="82%"/>
        <div style={{
          fontSize: 16, fontWeight: 500, color: "var(--fg)",
          paddingBottom: 10, lineHeight: 1,
        }}>{data.heroLabel}</div>
      </div>
    </CardShell>
  );
}

// ─────────────────────────────────────────────────────────────
// CARD 2 — Form & You
// ─────────────────────────────────────────────────────────────
function FormPill({ result }) {
  const map = {
    W: { bg: WIN_GREEN,   fg: "#0d0d0d" },
    L: { bg: LOSS_RED,    fg: "#ffffff" },
    D: { bg: DRAW_AMBER,  fg: "#0d0d0d" },
  };
  const c = map[result];
  return (
    <div style={{
      width: 40, height: 40, borderRadius: 999,
      background: c.bg, color: c.fg,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontWeight: 900, fontSize: 18,
      letterSpacing: "-0.02em",
      flex: "0 0 auto",
    }}>{result}</div>
  );
}
function CardForm() {
  const form = ["W", "W", "L", "W", "D"];
  return (
    <CardShell
      header="Form & You"
      subheader="Last 5 matches"
      narrativeIcon={<i className="ph ph-fire" style={{ fontSize: 20 }}/>}
      narrative="You've been scoring an avg of 1 goal per 147 mins recently. That's a hot streak — keep it going!"
      cta="View recent matches"
    >
      {/* Form indicators */}
      <div style={{
        marginTop: 12,
        display: "flex", gap: 9, alignItems: "center",
      }}>
        {form.map((r, i) => <FormPill key={i} result={r}/>)}
      </div>

      <div style={{
        marginTop: 12, marginBottom: 10,
        height: 1, background: "var(--border)",
      }}/>

      {/* Two stat lines */}
      <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
        {[
          { label: "Started", value: "5", sub: "of 5" },
          { label: "Played",  value: "440", sub: "min" },
          { label: "Goals",   value: "3",   sub: null },
          { label: "Assists", value: "1",   sub: null },
        ].map(({ label, value, sub }) => (
          <div key={label}>
            <div style={{
              fontSize: 10, fontWeight: 700, color: "var(--fg-muted)",
              letterSpacing: "0.18em", textTransform: "uppercase",
            }}>{label}</div>
            <div style={{
              marginTop: 2,
              fontWeight: 900, fontSize: 20, color: "var(--fg)",
              letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums",
            }}>{value}{sub && <span style={{ fontWeight: 500, color: "var(--fg-muted)", fontSize: 13 }}> {sub}</span>}</div>
          </div>
        ))}
      </div>
    </CardShell>
  );
}

// ─────────────────────────────────────────────────────────────
// CARD 3 — Where You Stand
// ─────────────────────────────────────────────────────────────
function CardStanding() {
  return (
    <CardShell
      header="Where You Stand"
      subheader="League scoring chart"
      narrativeIcon={<Pic.trophy size={20}/>}
      narrative={<>Joint top with <span style={{ fontWeight: 700 }}>Marcus Webb</span> of Bramall&nbsp;FC.</>}
      cta="View full statistics"
    >
      <div style={{ marginTop: 14, display: "flex", alignItems: "flex-end", gap: 8 }}>
        <LimeHero value="T-1st" fontSize={64} underlineWidth="86%"/>
      </div>
      <div style={{
        marginTop: 10,
        fontSize: 14, fontWeight: 500, color: "var(--fg)",
        letterSpacing: "-0.01em",
      }}>top scorer in your league</div>

      <div style={{
        marginTop: 12, marginBottom: 10,
        height: 1, background: "var(--border)",
      }}/>

      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{
          fontWeight: 900, fontSize: 24, color: "var(--fg)",
          letterSpacing: "-0.03em",
          fontVariantNumeric: "tabular-nums",
        }}>8</div>
        <div style={{
          fontSize: 10, fontWeight: 700, color: "var(--fg-muted)",
          letterSpacing: "0.16em", textTransform: "uppercase",
          lineHeight: 1.3,
        }}>goals<br/>this season</div>
      </div>
    </CardShell>
  );
}

// ─────────────────────────────────────────────────────────────
// CARD 4 — Market Value
// ─────────────────────────────────────────────────────────────
function Sparkline({ width = 290, height = 56 }) {
  // 12 data points showing a generally upward trend with subtle dips
  const pts = [38, 36, 40, 35, 42, 44, 41, 47, 50, 49, 54, 58];
  const max = Math.max(...pts), min = Math.min(...pts);
  const norm = pts.map(p => (p - min) / (max - min));
  const step = width / (pts.length - 1);
  const y = v => height - 6 - v * (height - 12);

  // Smooth path
  let d = `M 0 ${y(norm[0])}`;
  for (let i = 1; i < norm.length; i++) {
    const x0 = (i - 1) * step, x1 = i * step;
    const cx = (x0 + x1) / 2;
    d += ` C ${cx} ${y(norm[i-1])}, ${cx} ${y(norm[i])}, ${x1} ${y(norm[i])}`;
  }
  // Area fill path
  const dArea = d + ` L ${width} ${height} L 0 ${height} Z`;

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none"
         style={{ display: "block" }}>
      <defs>
        <linearGradient id="spark-fill" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%"  stopColor="#c8f135" stopOpacity="0.35"/>
          <stop offset="100%" stopColor="#c8f135" stopOpacity="0"/>
        </linearGradient>
      </defs>
      <path d={dArea} fill="url(#spark-fill)"/>
      <path d={d} fill="none" stroke="#c8f135" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
      {/* Last point dot */}
      <circle cx={width} cy={y(norm[norm.length-1])} r="3.5" fill="#c8f135"/>
    </svg>
  );
}

function CardMarket() {
  // Countdown to next update (live ticker)
  const [now, setNow] = React.useState(Date.now());
  React.useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);
  // Target ~18d 3h 23m 24s from "now"
  const targetRef = React.useRef(Date.now() + ((18*24 + 3)*3600 + 23*60 + 24) * 1000);
  const remaining = Math.max(0, targetRef.current - now);
  const days = Math.floor(remaining / 86400000);
  const hrs  = Math.floor((remaining % 86400000) / 3600000);
  const min  = Math.floor((remaining % 3600000) / 60000);
  const sec  = Math.floor((remaining % 60000) / 1000);
  const pad = n => String(n).padStart(2, "0");
  const countdown = `${pad(days)}:${pad(hrs)}:${pad(min)}:${pad(sec)}`;

  const animatedValue = useCountUp(24300, 1400);
  const formatted = Math.round(animatedValue).toLocaleString("en-GB");

  return (
    <CardShell
      header="Market Value"
      subheader="Updated weekly"
      narrativeIcon={<Pic.dollar size={20}/>}
      narrative={<>Up 4 weeks in a row. Highest of your career.<br/>2nd most valuable on your squad.</>}
      cta="See full trend"
    >
      <div style={{
        marginTop: 10,
        display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap",
      }}>
        <div style={{
          fontWeight: 900, fontSize: 38, color: "var(--fg)",
          letterSpacing: "-0.03em", lineHeight: 1,
          fontVariantNumeric: "tabular-nums",
        }}>£{formatted}</div>
        <div style={{
          fontSize: 12, fontWeight: 800, color: "var(--accent)",
          letterSpacing: "-0.01em",
          display: "inline-flex", alignItems: "baseline", gap: 3,
        }}>↗ +12.4% <span style={{ color: "var(--fg-muted)", fontWeight: 600 }}>this month</span></div>
      </div>

      {/* Sparkline */}
      <div style={{ marginTop: 8, marginRight: -2, marginLeft: -2 }}>
        <Sparkline width={290} height={40}/>
      </div>

      {/* Countdown pill */}
      <div style={{
        marginTop: 8,
        display: "inline-flex", alignSelf: "flex-start", alignItems: "center", gap: 7,
        background: "rgba(255,255,255,0.04)",
        border: "1px solid var(--border)",
        borderRadius: 999,
        padding: "4px 10px 4px 8px",
      }}>
        <span style={{
          width: 5, height: 5, borderRadius: 999, background: "var(--accent)",
          boxShadow: "0 0 8px var(--accent)",
        }}/>
        <span style={{
          fontSize: 9, fontWeight: 700, color: "var(--fg-muted)",
          letterSpacing: "0.16em", textTransform: "uppercase",
        }}>Next update</span>
        <span style={{
          fontSize: 11, fontWeight: 800, color: "var(--fg)",
          letterSpacing: "0.02em",
          fontVariantNumeric: "tabular-nums",
        }}>{countdown}</span>
      </div>
    </CardShell>
  );
}

// ─────────────────────────────────────────────────────────────
// Carousel + pagination dots
// ─────────────────────────────────────────────────────────────
function HeroCarousel({ briefingVariant }) {
  const scrollerRef = React.useRef(null);
  const [active, setActive] = React.useState(0);
  const cards = [
    () => <CardBriefing variant={briefingVariant}/>,
    CardForm,
    CardStanding,
    CardMarket,
  ];

  // ~90% of inner viewport, with small peek of neighbors
  const SCREEN_W = 390;
  const SIDE_PAD = 16;          // outer padding before first card
  const GAP = 12;                // gap between cards
  const PEEK = 18;               // how much next card peeks in
  const CARD_W = SCREEN_W - SIDE_PAD * 2 - PEEK; // ~322
  const CARD_H = 305;

  React.useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    const onScroll = () => {
      const i = Math.round(el.scrollLeft / (CARD_W + GAP));
      setActive(Math.max(0, Math.min(cards.length - 1, i)));
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  const scrollTo = (i) => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollTo({ left: i * (CARD_W + GAP), behavior: "smooth" });
  };

  return (
    <div>
      <div
        ref={scrollerRef}
        className="h-scroll carousel"
        style={{
          display: "flex",
          gap: GAP,
          overflowX: "auto",
          scrollSnapType: "x mandatory",
          paddingLeft: SIDE_PAD,
          paddingRight: SIDE_PAD,
          paddingBottom: 4,
        }}>
        {cards.map((C, i) => (
          <div key={i} style={{
            flex: `0 0 ${CARD_W}px`,
            height: CARD_H,
            scrollSnapAlign: "start",
            scrollSnapStop: "always",
          }}>
            <C/>
          </div>
        ))}
      </div>

      {/* Pagination dots */}
      <div style={{
        display: "flex", justifyContent: "center", gap: 8,
        marginTop: 16,
      }}>
        {cards.map((_, i) => {
          const isActive = i === active;
          return (
            <button key={i}
              onClick={() => scrollTo(i)}
              aria-label={`Card ${i + 1}`}
              style={{
                width: isActive ? 22 : 6,
                height: 6, borderRadius: 999,
                background: isActive ? "var(--accent)" : "rgba(255,255,255,0.22)",
                border: 0, padding: 0, cursor: "pointer",
                transition: "all 240ms cubic-bezier(0.2,0.7,0.2,1)",
              }}/>
          );
        })}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Quick-access scrolling row (existing pattern)
// ─────────────────────────────────────────────────────────────
function QuickAccess() {
  const items = [
    { key: "qa",     label: "Set up quick\naccess", Icon: Ic.bookmark, ghost: true },
    { key: "table",  label: "League\nTable",        Icon: Ic.table },
    { key: "refer",  label: "Refer a\nFriend",      Icon: Ic.refer },
    { key: "team",   label: "Team\nArea",           Icon: Ic.team },
    { key: "rank",   label: "League\nRankings",     Icon: Ic.trophy },
  ];
  return (
    <div className="h-scroll" style={{
      display: "flex", gap: 10,
      overflowX: "auto",
      padding: "0 16px",
      scrollSnapType: "x mandatory",
    }}>
      {items.map(({ key, label, Icon, ghost }) => (
        <div key={key} style={{
          flex: "0 0 auto",
          width: 96, height: 96,
          background: ghost ? "transparent" : "var(--surface)",
          border: ghost ? "1px dashed var(--border)" : "1px solid var(--border)",
          borderRadius: 12,
          padding: "10px 12px",
          display: "flex", flexDirection: "column", justifyContent: "space-between",
          position: "relative",
          scrollSnapAlign: "start",
          cursor: "pointer",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <Icon size={20} stroke="#ffffff"/>
            {!ghost && <Ic.arrowUR size={14} stroke="var(--fg-muted)" sw={1.8}/>}
          </div>
          <div style={{
            fontSize: 12, fontWeight: 700, color: "var(--fg)",
            lineHeight: 1.2, whiteSpace: "pre-line",
            letterSpacing: "-0.01em",
          }}>{label}</div>
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// League card
// ─────────────────────────────────────────────────────────────
function LeagueCard() {
  const rows = [
    { pos: 10, name: "Hucknall Town Reserves", pld: 25, gd: "-6",  pts: 25, you: false },
    { pos: 11, name: "Ravenshead FC",          pld: 26, gd: "-25", pts: 22, you: true  },
    { pos: 12, name: "Radc. Olympic FC",       pld: 26, gd: "-46", pts: 16, you: false },
  ];
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: 16, padding: "16px 16px 4px",
      marginInline: 16,
    }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: "var(--fg)", letterSpacing: "-0.01em" }}>
            Nottinghamshire Senior Football League
          </div>
          <Ic.arrowUR size={14} stroke="var(--fg-muted)" sw={1.8}/>
        </div>
      </div>
      <div style={{
        marginTop: 4,
        fontSize: 12, color: "var(--fg-muted)", fontWeight: 500,
      }}>NSL Division One · 2025/26</div>

      <div style={{ height: 14 }}/>

      {/* Column headers */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "24px 24px 1fr 32px 36px 32px",
        gap: 8,
        fontSize: 10, fontWeight: 700,
        color: "var(--fg-muted)",
        letterSpacing: "0.14em", textTransform: "uppercase",
        padding: "0 4px 8px",
        borderBottom: "1px solid var(--border)",
      }}>
        <div/>
        <div/>
        <div/>
        <div style={{ textAlign: "right" }}>PLD</div>
        <div style={{ textAlign: "right" }}>GD</div>
        <div style={{ textAlign: "right" }}>PTS</div>
      </div>

      {rows.map((r, i) => (
        <div key={r.pos} style={{
          display: "grid",
          gridTemplateColumns: "24px 24px 1fr 32px 36px 32px",
          gap: 8,
          padding: "12px 4px 12px",
          alignItems: "center",
          borderLeft: r.you ? "2px solid var(--accent)" : "2px solid transparent",
          paddingLeft: r.you ? 8 : 4,
          marginLeft: r.you ? -4 : 0,
          borderBottom: i < rows.length - 1 ? "1px solid var(--border)" : "0",
        }}>
          <div style={{
            fontSize: 13, fontWeight: 700,
            color: r.you ? "var(--accent)" : "var(--fg)",
            fontVariantNumeric: "tabular-nums",
          }}>{r.pos}</div>
          <Ic.minus size={16} stroke="var(--fg-muted)" sw={1.6}/>
          <div style={{
            fontSize: 14, fontWeight: r.you ? 700 : 500,
            color: "var(--fg)",
            whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
          }}>{r.name}</div>
          <div style={{
            textAlign: "right", fontSize: 13, fontWeight: 500,
            color: "var(--fg-muted)", fontVariantNumeric: "tabular-nums",
          }}>{r.pld}</div>
          <div style={{
            textAlign: "right", fontSize: 13, fontWeight: 500,
            color: "var(--fg-muted)", fontVariantNumeric: "tabular-nums",
          }}>{r.gd}</div>
          <div style={{
            textAlign: "right", fontSize: 14, fontWeight: 900,
            color: "var(--fg)", fontVariantNumeric: "tabular-nums",
            letterSpacing: "-0.01em",
          }}>{r.pts}</div>
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Newsfeed — header + posts
// ─────────────────────────────────────────────────────────────
function NewsfeedHeader() {
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "0 16px",
    }}>
      <div style={{
        fontSize: 26, fontWeight: 900, color: "var(--fg)",
        letterSpacing: "-0.02em", textTransform: "uppercase",
      }}>Newsfeed</div>
    </div>
  );
}

function ReactionEmoji({ children, bg }) {
  return (
    <div style={{
      width: 22, height: 22, borderRadius: 999,
      background: bg,
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      fontSize: 12, marginLeft: -6,
      border: "1.5px solid var(--surface)",
    }}>{children}</div>
  );
}

function NewsCard({ org, time, title, body, imgKind, reactionCount, fullTime }) {
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: 16, padding: "14px 16px",
      marginInline: 16,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 26, height: 26, borderRadius: 999,
          background: "#3b2a5a", color: "#c4a5ff",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontWeight: 900, fontSize: 11,
        }}>
          <Sicon size={14} stroke="#c4a5ff" sw={1.8}><circle cx="12" cy="8" r="4"/><path d="M5 21a7 7 0 0114 0"/></Sicon>
        </div>
        <div style={{ fontSize: 13, fontWeight: 700, color: "var(--fg)" }}>{org}</div>
      </div>
      <div style={{
        marginTop: 4, marginLeft: 36,
        fontSize: 12, fontWeight: 500, color: "var(--fg-muted)",
      }}>{time}</div>

      <div style={{ height: 12 }}/>

      <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          {fullTime ? (
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 6,
              fontSize: 13, fontWeight: 900, color: "#ef4444",
              letterSpacing: "0.04em",
            }}>
              <span style={{ color: "#ef4444" }}>!</span> FULL TIME <span style={{ color: "#ef4444" }}>!</span>
            </div>
          ) : (
            <div style={{
              fontSize: 14, fontWeight: 800, color: "var(--fg)",
              letterSpacing: "-0.01em", lineHeight: 1.25,
              display: "flex", alignItems: "center", gap: 6,
            }}>
              <Ic.ball size={14} stroke="var(--fg)" sw={1.6}/>
              {title}
              <Ic.ball size={14} stroke="var(--fg)" sw={1.6}/>
            </div>
          )}
          {body && (
            <div style={{
              marginTop: 8,
              fontSize: 13, fontWeight: 400, color: "var(--fg)",
              lineHeight: 1.45,
            }}>{body}</div>
          )}
        </div>

        {/* Image placeholder */}
        <div style={{
          flex: "0 0 auto",
          width: 86, height: 86, borderRadius: 10,
          background: imgKind === "schedule"
            ? "linear-gradient(135deg, #2a2a2a, #1a1a1a)"
            : "linear-gradient(135deg, #5a1e1e, #c84545 60%, #1a1a1a)",
          position: "relative",
          overflow: "hidden",
          border: "1px solid var(--border)",
        }}>
          {imgKind === "schedule" ? (
            <div style={{
              position: "absolute", inset: 0,
              display: "flex", alignItems: "flex-end", justifyContent: "center",
              padding: 6,
              color: "#fff", fontWeight: 900, fontSize: 14,
              letterSpacing: "-0.01em",
              textShadow: "0 1px 2px rgba(0,0,0,0.5)",
            }}>SCHEDULE</div>
          ) : (
            <>
              <div style={{
                position: "absolute", left: 4, top: 4,
                writingMode: "vertical-rl", transform: "rotate(180deg)",
                fontSize: 9, fontWeight: 900, color: "#fff",
                letterSpacing: "0.18em",
              }}>FT</div>
              <div style={{
                position: "absolute", inset: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                gap: 6,
                fontWeight: 900, color: "#fff",
              }}>
                <span style={{ fontSize: 24, lineHeight: 1 }}>6</span>
                <span style={{ fontSize: 11, opacity: 0.8 }}>·</span>
                <span style={{ fontSize: 24, lineHeight: 1 }}>2</span>
              </div>
            </>
          )}
        </div>
      </div>

      {reactionCount != null && (
        <>
          <div style={{ height: 12, borderBottom: "1px solid var(--border)", marginTop: 10 }}/>
          <div style={{
            marginTop: 10,
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Ic.thumb size={18} stroke="var(--fg)" sw={1.8}/>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--fg)" }}>Like</div>
              <div style={{ display: "flex", alignItems: "center", marginLeft: 6 }}>
                <ReactionEmoji bg="#f5b53b">👍</ReactionEmoji>
                <ReactionEmoji bg="#ef4444">🔥</ReactionEmoji>
                <ReactionEmoji bg="#ef4444">❤️</ReactionEmoji>
                <div style={{ marginLeft: 4, fontSize: 12, fontWeight: 700, color: "var(--fg)" }}>{reactionCount}</div>
              </div>
            </div>
            <div style={{
              display: "flex", alignItems: "center", gap: 6,
              fontSize: 13, fontWeight: 500, color: "var(--fg)",
            }}>
              <Sicon size={16} stroke="var(--fg)" sw={1.8}><circle cx="6" cy="12" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><path d="M8 11l8-4M8 13l8 4"/></Sicon>
              Share
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Newsfeed() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <NewsfeedHeader/>
      <NewsCard
        org="Men - Nottinghamshire Senior Football League"
        time="acunitedfc · 14 hours ago"
        title="WEEKEND MATCH SCHEDULE"
        body="A huge weekend of football ahead as our senior sides take the field across Saturday and Sunday. For all other matches, be sure to chec…"
        imgKind="schedule"
        reactionCount={7}
      />
      <NewsCard
        org="Men - Nottinghamshire Senior Football League"
        time="rofc1876 · 1 day ago"
        fullTime
        body="RvFC U23 6–2 Southern Town U23"
        imgKind="score"
      />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Bottom tab bar (Base / Matches / Team / League / Profile)
// ─────────────────────────────────────────────────────────────
function TabBar() {
  const items = [
    { key: "base",   label: "Base",    Icon: Ic.ic_base,   active: true  },
    { key: "match",  label: "Matches", Icon: Ic.ic_match,  active: false },
    { key: "team",   label: "Team",    Icon: Ic.ic_team,   active: false },
    { key: "league", label: "League",  Icon: Ic.ic_league, active: false },
    { key: "prof",   label: "Profile", Icon: Ic.ic_prof,   active: false },
  ];
  return (
    <div style={{
      position: "absolute", left: 0, right: 0, bottom: 0,
      height: 68,
      background: "var(--bg)",
      borderTop: "1px solid var(--border)",
      display: "flex", alignItems: "center",
      paddingBottom: "calc(env(safe-area-inset-bottom, 0px))",
      zIndex: 5,
    }}>
      {items.map(({ key, label, Icon, active }) => (
        <button key={key} style={{
          flex: 1, height: "100%",
          background: "transparent", border: 0,
          display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", gap: 4,
          color: active ? "var(--fg)" : "var(--fg-muted)",
          cursor: "pointer",
        }}>
          <Icon size={22} sw={active ? 2 : 1.6}/>
          <div style={{
            fontSize: 11, fontWeight: active ? 800 : 600,
            letterSpacing: "-0.01em",
          }}>{label}</div>
        </button>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// App shell
// ─────────────────────────────────────────────────────────────
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "briefingVariant": "won"
}/*EDITMODE-END*/;

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  return (
    <>
      <div className="scroll-area" style={{ paddingTop: 44, paddingBottom: 96 }}
           data-screen-label="Base · Home">
        <TopBar/>
        <Greeting name="Lewis Bilbie"/>

        {/* NEW — 4-card carousel hero */}
        <HeroCarousel briefingVariant={t.briefingVariant}/>

        <div style={{ display: "flex", flexDirection: "column", gap: 24, marginTop: 24 }}>
          <QuickAccess/>
          <div>
            <div style={{
              fontSize: 26, fontWeight: 900, color: "var(--fg)",
              letterSpacing: "-0.02em", textTransform: "uppercase",
              padding: "0 16px 14px",
            }}>League Table</div>
            <LeagueCard/>
          </div>
          <Newsfeed/>
        </div>
        <div style={{ height: 24 }}/>
      </div>
      <TabBar/>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Card 1 — Post-Match Briefing">
          <TweakRadio
            label="Result variant"
            value={t.briefingVariant}
            options={[
              { value: "won",  label: "Won · hat trick" },
              { value: "lost", label: "Lost · sub impact" },
            ]}
            onChange={(v) => setTweak("briefingVariant", v)}
          />
        </TweakSection>
      </TweaksPanel>
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
