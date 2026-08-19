import { useCallback, useEffect, useRef, useState } from "react";

import type { NotificationItem, ServerMessage } from "../types";

const WS_URL = import.meta.env.VITE_WS_URL;
const MAX_BACKOFF_MS = 30_000;

export function useWebSocket() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      backoffRef.current = 1000;
      setConnected(true);
      ws.send(JSON.stringify({ type: "subscribe", interval_seconds: 30, enabled_types: ["overdue", "due_soon"] }));
    };

    ws.onmessage = (event) => {
      try {
        const message: ServerMessage = JSON.parse(event.data);
        if (message.type === "notification_batch") {
          setNotifications(message.notifications);
        }
      } catch {
        // ignore malformed messages
      }
    };

    ws.onclose = () => {
      setConnected(false);
      if (!mountedRef.current) return;
      reconnectTimerRef.current = setTimeout(connect, backoffRef.current);
      backoffRef.current = Math.min(backoffRef.current * 2, MAX_BACKOFF_MS);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendAck = useCallback((notificationId: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
    wsRef.current?.send(JSON.stringify({ type: "ack", notification_id: notificationId }));
  }, []);

  return { notifications, connected, sendAck };
}
