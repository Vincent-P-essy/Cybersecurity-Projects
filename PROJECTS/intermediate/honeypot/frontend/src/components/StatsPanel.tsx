import type { Stats } from "../lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const SERVICE_COLORS: Record<string, string> = {
  ssh: "#e94560",
  http: "#f5a623",
  ftp: "#4ecdc4",
};

interface Props {
  stats: Stats | null;
}

export default function StatsPanel({ stats }: Props) {
  if (!stats) return <p style={{ color: "#888" }}>Loading stats…</p>;

  const serviceData = Object.entries(stats.by_service).map(([name, value]) => ({ name, value }));

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "24px" }}>
        <StatCard label="Total Events" value={stats.total_events} color="#e94560" />
        <StatCard label="Unique IPs" value={stats.unique_ips} color="#f5a623" />
        <StatCard label="Max Threat Score" value={`${stats.max_threat_score}/100`} color="#c0392b" />
        <StatCard label="Services Active" value={Object.keys(stats.by_service).length} color="#4ecdc4" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
        <Panel title="Attacks by Service">
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={serviceData}>
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ background: "#16213e", border: "none" }} />
              <Bar dataKey="value">
                {serviceData.map((entry) => (
                  <Cell key={entry.name} fill={SERVICE_COLORS[entry.name] ?? "#888"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Top Usernames">
          <TopList items={stats.top_usernames.map((x) => ({ label: x.username, count: x.count }))} />
        </Panel>

        <Panel title="Top Countries">
          <TopList items={stats.top_countries.map((x) => ({ label: x.country, count: x.count }))} />
        </Panel>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div style={{ background: "#16213e", padding: "20px", borderRadius: "8px", borderLeft: `4px solid ${color}` }}>
      <div style={{ color: "#888", fontSize: "13px", marginBottom: "8px" }}>{label}</div>
      <div style={{ color: "#eee", fontSize: "26px", fontWeight: 700 }}>{value}</div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: "#16213e", padding: "16px", borderRadius: "8px" }}>
      <h3 style={{ color: "#e94560", fontSize: "14px", marginBottom: "12px", margin: "0 0 12px 0" }}>{title}</h3>
      {children}
    </div>
  );
}

function TopList({ items }: { items: { label: string; count: number }[] }) {
  return (
    <ol style={{ margin: 0, paddingLeft: "18px", color: "#eee", fontSize: "13px" }}>
      {items.slice(0, 8).map((item, i) => (
        <li key={i} style={{ marginBottom: "6px", display: "flex", justifyContent: "space-between" }}>
          <span style={{ fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "160px" }}>
            {item.label}
          </span>
          <span style={{ color: "#e94560", fontWeight: 600, marginLeft: "8px" }}>{item.count}</span>
        </li>
      ))}
    </ol>
  );
}
