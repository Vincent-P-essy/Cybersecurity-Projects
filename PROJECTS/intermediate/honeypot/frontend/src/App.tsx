import { useEffect, useState } from "react";
import type { HoneypotEvent, Stats } from "./lib/api";
import { fetchEvents, fetchStats } from "./lib/api";
import EventFeed from "./components/EventFeed";
import StatsPanel from "./components/StatsPanel";

const TABS = ["Live Feed", "Statistics"] as const;
type Tab = (typeof TABS)[number];

export default function App() {
  const [tab, setTab] = useState<Tab>("Live Feed");
  const [stats, setStats] = useState<Stats | null>(null);
  const [events, setEvents] = useState<HoneypotEvent[]>([]);

  useEffect(() => {
    const load = async () => {
      const [s, e] = await Promise.all([fetchStats(), fetchEvents()]);
      setStats(s);
      setEvents(e.events);
    };
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#1a1a2e", color: "#eee", fontFamily: "Arial, sans-serif" }}>
      <header style={{ background: "#16213e", padding: "0 24px", display: "flex", alignItems: "center", borderBottom: "2px solid #e94560", gap: "24px" }}>
        <div style={{ padding: "16px 0" }}>
          <span style={{ color: "#e94560", fontSize: "22px", fontWeight: 700, letterSpacing: "2px" }}>CANARIS</span>
          <span style={{ color: "#888", fontSize: "13px", marginLeft: "10px" }}>honeypot dashboard</span>
        </div>
        <nav style={{ display: "flex", gap: "4px", marginLeft: "auto" }}>
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                background: tab === t ? "#e94560" : "transparent",
                color: tab === t ? "#fff" : "#aaa",
                border: "none",
                padding: "8px 18px",
                borderRadius: "4px",
                cursor: "pointer",
                fontWeight: tab === t ? 700 : 400,
                fontSize: "14px",
              }}
            >
              {t}
            </button>
          ))}
        </nav>
        {stats && (
          <div style={{ display: "flex", gap: "20px", marginLeft: "16px" }}>
            <Indicator label="Events" value={stats.total_events} />
            <Indicator label="IPs" value={stats.unique_ips} />
          </div>
        )}
      </header>

      <main style={{ padding: "24px" }}>
        {tab === "Live Feed" && <EventFeed initialEvents={events} />}
        {tab === "Statistics" && <StatsPanel stats={stats} />}
      </main>
    </div>
  );
}

function Indicator({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ color: "#e94560", fontWeight: 700, fontSize: "18px" }}>{value}</div>
      <div style={{ color: "#888", fontSize: "11px" }}>{label}</div>
    </div>
  );
}
