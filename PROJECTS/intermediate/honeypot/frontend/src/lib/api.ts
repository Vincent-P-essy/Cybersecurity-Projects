const BASE = import.meta.env.VITE_API_URL ?? "";

export interface HoneypotEvent {
  id: number;
  service: "ssh" | "http" | "ftp";
  source_ip: string;
  source_port: number;
  username: string | null;
  password: string | null;
  command: string | null;
  path: string | null;
  user_agent: string | null;
  country: string | null;
  city: string | null;
  threat_score: number;
  created_at: string;
}

export interface Stats {
  total_events: number;
  unique_ips: number;
  max_threat_score: number;
  by_service: Record<string, number>;
  top_ips: { ip: string; count: number }[];
  top_usernames: { username: string; count: number }[];
  top_passwords: { password: string; count: number }[];
  top_countries: { country: string; count: number }[];
}

export async function fetchStats(): Promise<Stats> {
  const r = await fetch(`${BASE}/api/stats`);
  return r.json();
}

export async function fetchEvents(page = 1, limit = 50): Promise<{ events: HoneypotEvent[]; total: number }> {
  const r = await fetch(`${BASE}/api/events?page=${page}&limit=${limit}`);
  return r.json();
}

export function openEventStream(onEvent: (e: HoneypotEvent) => void): EventSource {
  const es = new EventSource(`${BASE}/api/events/stream`);
  es.onmessage = (msg) => {
    try {
      onEvent(JSON.parse(msg.data));
    } catch {
      /* ping */
    }
  };
  return es;
}
