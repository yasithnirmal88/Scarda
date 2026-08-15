import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './useAuth';

/**
 * Derives the WebSocket URL from the API base URL.
 * The backend mounts the WebSocket endpoint at ``/api/ws``.
 */
function wsUrl(): string {
  const base = (import.meta.env.VITE_API_URL as string | undefined) || '/api';
  if (base.startsWith('http')) {
    // http(s)://host/api → ws(s)://host/api/ws
    const ws = base.replace(/^http/, 'ws');
    return ws.endsWith('/api') ? `${ws}/ws` : `${ws}/ws`;
  }
  // Relative path on same origin
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const path = base.endsWith('/api') ? `${base}/ws` : `${base}/ws`;
  return `${proto}://${window.location.host}${path}`;
}

export interface LiveReading {
  string_id?: string;
  power_w?: number;
  voltage_v?: number;
  current_a?: number;
  irradiance_wpm2?: number;
  temperature_c?: number;
  timestamp?: string;
  total_power_kw?: number;
}

export interface LiveWeather {
  temperature_c?: number;
  irradiance_wpm2?: number;
  humidity_pct?: number;
  wind_speed_mps?: number;
  timestamp?: string;
}

export interface LiveAlert {
  alert_id: string;
  string_id: string;
  alert_type: string;
  severity: string;
  reason: string;
  expected_value?: number;
  actual_value?: number;
  deviation_pct?: number;
}

type WsStatus = 'connecting' | 'open' | 'closed';

interface UseWebSocketResult {
  status: WsStatus;
  lastReading: LiveReading | null;
  lastWeather: LiveWeather | null;
  alerts: LiveAlert[];
  lastUpdated: Date | null;
}

/**
 * Subscribes to the Scarda WebSocket and exposes live 10-min updates
 * (readings, weather, alerts) pushed by the backend scheduler. The frontend
 * never fabricates these — they originate from the data provider.
 */
export function useLiveData(): UseWebSocketResult {
  const { token } = useAuth();
  const [status, setStatus] = useState<WsStatus>('closed');
  const [lastReading, setLastReading] = useState<LiveReading | null>(null);
  const [lastWeather, setLastWeather] = useState<LiveWeather | null>(null);
  const [alerts, setAlerts] = useState<LiveAlert[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const handle = useCallback((msg: { type: string; payload?: unknown }) => {
    if (msg.type === 'new_reading' && msg.payload) {
      const p = msg.payload as Record<string, unknown>;
      const readings = (p.readings as LiveReading[] | undefined) ?? [];
      setLastReading(readings[0] ?? (p as LiveReading));
      setLastUpdated(new Date());
    } else if (msg.type === 'weather_update' && msg.payload) {
      setLastWeather(msg.payload as LiveWeather);
      setLastUpdated(new Date());
    } else if (msg.type === 'alert_created' && msg.payload) {
      setAlerts((prev) => [msg.payload as LiveAlert, ...prev].slice(0, 50));
      setLastUpdated(new Date());
    } else if (msg.type === 'alert_resolved' && msg.payload) {
      const a = msg.payload as LiveAlert;
      setAlerts((prev) => prev.filter((x) => x.alert_id !== a.alert_id));
    }
  }, []);

  useEffect(() => {
    let closed = false;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;

    const connect = () => {
      if (closed) return;
      const url = wsUrl();
      let ws: WebSocket;
      try {
        ws = token ? new WebSocket(url, [token]) : new WebSocket(url);
      } catch {
        return;
      }
      wsRef.current = ws;
      setStatus('connecting');

      ws.onopen = () => {
        setStatus('open');
        // Subscribe to all live topics.
        ['readings', 'weather', 'alerts'].forEach((topic) =>
          ws.send(JSON.stringify({ type: 'subscribe', topic })),
        );
      };
      ws.onmessage = (ev) => {
        try {
          handle(JSON.parse(ev.data) as { type: string; payload?: unknown });
        } catch {
          /* ignore malformed frames */
        }
      };
      ws.onclose = () => {
        setStatus('closed');
        if (!closed) reconnectTimer = setTimeout(connect, 5000);
      };
      ws.onerror = () => {
        setStatus('closed');
        try {
          ws.close();
        } catch {
          /* noop */
        }
      };
    };

    connect();
    return () => {
      closed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      try {
        wsRef.current?.close();
      } catch {
        /* noop */
      }
    };
  }, [token, handle]);

  return { status, lastReading, lastWeather, alerts, lastUpdated };
}
