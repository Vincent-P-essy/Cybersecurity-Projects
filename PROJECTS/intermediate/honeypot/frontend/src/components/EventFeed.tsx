import { useEffect, useRef, useState } from "react";
import type { HoneypotEvent } from "../lib/api";
import { openEventStream } from "../lib/api";

const SERVICE_COLOR: Record<string, string> = {
  ssh: "#e94560",
  http: "#f5a623",
  ftp: "#4ecdc4",
};

function scoreColor(score: number): string {
  if (score >= 70) return "#e94560";
  if (score >= 40) return "#f5a623";
  return "#4ecdc4";
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString();
}

function EventRow({ ev }: { ev: HoneypotEvent }) {
  const detail =
    ev.service === "ssh"
      ? ev.command
        ? `cmd: ${ev.command}`
        : `auth: ${ev.username}/${ev.password}`
      : ev.service === "ftp"
      ? `auth: ${ev.username}/${ev.password}`
      : `${ev.path ?? "/"}`;

  return (
    <tr style={{ borderBottom: "1px solid #1a1a2e" }}>
      <td style={{ padding: "8px 10px", color: SERVICE_COLOR[ev.service], fontWeight: 700, width: "60px" }}>
        {ev.service.toUpperCase()}
      </td>
      <td style={{ padding: "8px 10px", fontFamily: "monospace", color: "#eee" }}>{ev.source_ip}</td>
      <td style={{ padding: "8px 10px", color: "#aaa" }}>
        {ev.country ?? "?"} {ev.city ? `(${ev.city})` : ""}
      </td>
      <td style={{ padding: "8px 10px", fontFamily: "monospace", color: "#ccc", maxWidth: "280px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {detail}
      </td>
      <td style={{ padding: "8px 10px", textAlign: "center" }}>
        <span style={{ color: scoreColor(ev.threat_score ?? 0), fontWeight: 700 }}>{ev.threat_score ?? 0}</span>
      </td>
      <td style={{ padding: "8px 10px", color: "#666", fontSize: "12px", whiteSpace: "nowrap" }}>
        {ev.created_at ? formatTime(ev.created_at) : "—"}
      </td>
    </tr>
  );
}

interface Props {
  initialEvents: HoneypotEvent[];
}

export default function EventFeed({ initialEvents }: Props) {
  const [events, setEvents] = useState<HoneypotEvent[]>(initialEvents);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    setEvents(initialEvents);
  }, [initialEvents]);

  useEffect(() => {
    const es = openEventStream((ev) => {
      setEvents((prev) => [{ ...ev, id: Date.now(), created_at: new Date().toISOString() } as HoneypotEvent, ...prev.slice(0, 199)]);
    });
    esRef.current = es;
    return () => es.close();
  }, []);

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
        <thead>
          <tr style={{ background: "#0f3460", color: "#aaa", textAlign: "left" }}>
            <th style={{ padding: "10px" }}>Service</th>
            <th style={{ padding: "10px" }}>Source IP</th>
            <th style={{ padding: "10px" }}>Location</th>
            <th style={{ padding: "10px" }}>Detail</th>
            <th style={{ padding: "10px", textAlign: "center" }}>Score</th>
            <th style={{ padding: "10px" }}>Time</th>
          </tr>
        </thead>
        <tbody>
          {events.length === 0 ? (
            <tr>
              <td colSpan={6} style={{ textAlign: "center", color: "#666", padding: "40px" }}>
                Waiting for honeypot activity…
              </td>
            </tr>
          ) : (
            events.map((ev) => <EventRow key={ev.id} ev={ev} />)
          )}
        </tbody>
      </table>
    </div>
  );
}
