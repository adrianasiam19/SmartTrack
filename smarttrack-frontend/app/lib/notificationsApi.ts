/**
 * In-app notifications API client (Stage 6 shape)
 */
import { fetchWithAuth } from './authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export type NotificationCategory =
  | 'achievement'
  | 'xp'
  | 'learning'
  | 'recommendation'
  | 'progress'
  | 'system'
  | 'streak'
  | 'reminder';

/** @deprecated use NotificationCategory */
export type NotificationType = NotificationCategory;

export type AppNotification = {
  id: string;
  user_id?: string | null;
  title: string;
  message: string;
  category: NotificationCategory | string;
  type: NotificationCategory | string;
  created_at: string;
  read_status: boolean;
  is_read: boolean;
  action_link?: string | null;
  priority?: 'low' | 'normal' | 'high' | 'urgent' | string;
  priority_value?: number;
  data?: Record<string, unknown> | null;
};

export type NotificationList = {
  notifications: AppNotification[];
  unread_count: number;
};

export async function fetchNotifications(options?: {
  limit?: number;
  unreadOnly?: boolean;
  category?: string;
}): Promise<NotificationList> {
  const params = new URLSearchParams({
    limit: String(options?.limit ?? 40),
  });
  if (options?.unreadOnly) params.set('unread_only', 'true');
  if (options?.category) params.set('category', options.category);
  const res = await fetchWithAuth(`${API_BASE}/notifications?${params}`);
  if (!res.ok) throw new Error('Failed to load notifications');
  return res.json();
}

export async function fetchUnreadNotificationCount(): Promise<number> {
  const res = await fetchWithAuth(`${API_BASE}/notifications/unread-count`);
  if (!res.ok) return 0;
  const body = await res.json();
  return Number(body.unread_count || 0);
}

export async function markNotificationRead(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}/notifications/${encodeURIComponent(id)}/read`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to mark notification as read');
}

export async function markAllNotificationsRead(): Promise<number> {
  const res = await fetchWithAuth(`${API_BASE}/notifications/read-all`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to mark all as read');
  const body = await res.json();
  return Number(body.updated || 0);
}

/** Stage 6 monitor — learner activity signals for the notification engine. */
export async function fetchNotificationActivitySnapshot(): Promise<Record<string, unknown>> {
  const res = await fetchWithAuth(`${API_BASE}/notifications/activity-snapshot`);
  if (!res.ok) throw new Error('Failed to load activity snapshot');
  const body = await res.json();
  return (body?.snapshot || {}) as Record<string, unknown>;
}

/** Stage 7 — force-run intelligent notification rules for the current user. */
export async function runNotificationEngine(force = false): Promise<{
  ran: boolean;
  created: number;
  rules_fired: string[];
}> {
  const params = new URLSearchParams();
  if (force) params.set('force', 'true');
  const qs = params.toString();
  const res = await fetchWithAuth(
    `${API_BASE}/notifications/engine/run${qs ? `?${qs}` : ''}`,
    { method: 'POST' },
  );
  if (!res.ok) throw new Error('Failed to run notification engine');
  return res.json();
}

/** Stage 9 — inspect generation vs delivery architecture (no Firebase send). */
export async function fetchNotificationDeliveryArchitecture(): Promise<{
  generation: string;
  delivery: string;
  active_channels: string[];
  push_notifications_enabled: boolean;
  fcm_credentials_configured: boolean;
  web_push_vapid_configured: boolean;
}> {
  const res = await fetchWithAuth(`${API_BASE}/notifications/delivery-architecture`);
  if (!res.ok) throw new Error('Failed to load delivery architecture');
  return res.json();
}

/** Stage 9 — store an FCM / Web Push token for later (send not implemented). */
export async function registerPushToken(input: {
  provider: 'fcm' | 'web_push' | string;
  token: string;
  platform?: string;
  endpoint_meta?: Record<string, unknown>;
}): Promise<{ push_enabled: boolean }> {
  const res = await fetchWithAuth(`${API_BASE}/notifications/push-tokens`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error('Failed to register push token');
  return res.json();
}

export async function deactivatePushToken(input: {
  token: string;
  provider?: string;
}): Promise<number> {
  const res = await fetchWithAuth(`${API_BASE}/notifications/push-tokens`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error('Failed to deactivate push token');
  const body = await res.json();
  return Number(body.deactivated || 0);
}
