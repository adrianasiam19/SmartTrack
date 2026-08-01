/**
 * In-app notifications API client
 */
import { fetchWithAuth } from './authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export type NotificationType =
  | 'achievement'
  | 'xp'
  | 'learning'
  | 'recommendation'
  | 'progress'
  | 'system';

export type AppNotification = {
  id: string;
  title: string;
  message: string;
  type: NotificationType | string;
  is_read: boolean;
  data?: Record<string, unknown> | null;
  created_at: string;
};

export type NotificationList = {
  notifications: AppNotification[];
  unread_count: number;
};

export async function fetchNotifications(options?: {
  limit?: number;
  unreadOnly?: boolean;
}): Promise<NotificationList> {
  const params = new URLSearchParams({
    limit: String(options?.limit ?? 40),
  });
  if (options?.unreadOnly) params.set('unread_only', 'true');
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
