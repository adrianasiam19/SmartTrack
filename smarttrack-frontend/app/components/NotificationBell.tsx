'use client';

/**
 * Stage 8 — Notification User Interface
 *
 * Mounted on the Dashboard only. Shows unread badge, opens a panel
 * sorted newest-first, highlights unread rows, marks read on open,
 * and navigates via action_link when present.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Award,
  Bell,
  BookOpen,
  CheckCheck,
  ChevronRight,
  Lightbulb,
  Loader2,
  Sparkles,
  Star,
  Trophy,
  AlertTriangle,
} from 'lucide-react';
import { getAccessToken } from '../lib/authApi';
import {
  fetchNotifications,
  fetchUnreadNotificationCount,
  markAllNotificationsRead,
  markNotificationRead,
  type AppNotification,
  type NotificationType,
} from '../lib/notificationsApi';

const POLL_MS = 45_000;

function typeMeta(type: string) {
  const t = type as NotificationType;
  switch (t) {
    case 'achievement':
      return {
        label: 'Achievement',
        icon: Trophy,
        chip: 'bg-amber-50 text-amber-700',
        iconWrap: 'bg-amber-100 text-amber-700',
      };
    case 'xp':
      return {
        label: 'XP',
        icon: Award,
        chip: 'bg-violet-50 text-violet-700',
        iconWrap: 'bg-violet-100 text-violet-700',
      };
    case 'learning':
      return {
        label: 'Learning',
        icon: BookOpen,
        chip: 'bg-sky-50 text-sky-700',
        iconWrap: 'bg-sky-100 text-sky-700',
      };
    case 'recommendation':
      return {
        label: 'Recommendation',
        icon: Lightbulb,
        chip: 'bg-indigo-50 text-indigo-700',
        iconWrap: 'bg-indigo-100 text-indigo-700',
      };
    case 'progress':
      return {
        label: 'Progress',
        icon: Star,
        chip: 'bg-emerald-50 text-emerald-700',
        iconWrap: 'bg-emerald-100 text-emerald-700',
      };
    case 'streak':
      return {
        label: 'Streak',
        icon: Sparkles,
        chip: 'bg-orange-50 text-orange-700',
        iconWrap: 'bg-orange-100 text-orange-700',
      };
    case 'reminder':
      return {
        label: 'Reminder',
        icon: Bell,
        chip: 'bg-rose-50 text-rose-700',
        iconWrap: 'bg-rose-100 text-rose-700',
      };
    case 'system':
    default:
      return {
        label: 'System',
        icon: AlertTriangle,
        chip: 'bg-slate-100 text-slate-600',
        iconWrap: 'bg-slate-100 text-slate-600',
      };
  }
}

function isUnread(item: AppNotification) {
  return !(item.read_status ?? item.is_read);
}

function actionHref(item: AppNotification): string | null {
  if (typeof item.action_link === 'string' && item.action_link.trim()) {
    return item.action_link.trim();
  }
  if (typeof item.data?.href === 'string' && item.data.href.trim()) {
    return item.data.href.trim();
  }
  return null;
}

function sortNewestFirst(list: AppNotification[]) {
  return [...list].sort((a, b) => {
    const ta = new Date(a.created_at).getTime();
    const tb = new Date(b.created_at).getTime();
    return (Number.isFinite(tb) ? tb : 0) - (Number.isFinite(ta) ? ta : 0);
  });
}

function formatWhen(iso: string) {
  try {
    const date = new Date(iso);
    const diffMs = Date.now() - date.getTime();
    const mins = Math.floor(diffMs / 60_000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
}

export default function NotificationBell() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<AppNotification[]>([]);
  const [unread, setUnread] = useState(0);
  const panelRef = useRef<HTMLDivElement>(null);

  const refreshCount = useCallback(async () => {
    if (!getAccessToken()) {
      setUnread(0);
      return;
    }
    try {
      const count = await fetchUnreadNotificationCount();
      setUnread(count);
    } catch {
      /* ignore */
    }
  }, []);

  const loadList = useCallback(async () => {
    if (!getAccessToken()) return;
    setLoading(true);
    try {
      const data = await fetchNotifications({ limit: 40 });
      setItems(sortNewestFirst(data.notifications || []));
      setUnread(data.unread_count);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshCount();
    const id = window.setInterval(() => void refreshCount(), POLL_MS);
    const onFocus = () => void refreshCount();
    window.addEventListener('focus', onFocus);
    return () => {
      window.clearInterval(id);
      window.removeEventListener('focus', onFocus);
    };
  }, [refreshCount]);

  useEffect(() => {
    if (open) void loadList();
  }, [open, loadList]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClick);
      document.removeEventListener('keydown', onKey);
    };
  }, []);

  const onOpenItem = async (item: AppNotification) => {
    if (isUnread(item)) {
      try {
        await markNotificationRead(item.id);
        setItems((prev) =>
          prev.map((n) =>
            n.id === item.id ? { ...n, is_read: true, read_status: true } : n,
          ),
        );
        setUnread((c) => Math.max(0, c - 1));
      } catch {
        /* ignore */
      }
    }
    const href = actionHref(item);
    setOpen(false);
    if (href) router.push(href);
  };

  const onMarkAll = async () => {
    try {
      await markAllNotificationsRead();
      setItems((prev) =>
        prev.map((n) => ({ ...n, is_read: true, read_status: true })),
      );
      setUnread(0);
    } catch {
      /* ignore */
    }
  };

  return (
    <div ref={panelRef} className="fixed top-4 right-4 z-50">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="relative flex items-center justify-center w-11 h-11 bg-white border border-[#BFDBFE] rounded-xl shadow-md shadow-[#2563EB]/10 text-[#2563EB] hover:bg-[#EFF6FF] hover:shadow-lg active:scale-95 transition-all"
        aria-label={unread > 0 ? `Notifications, ${unread} unread` : 'Notifications'}
        aria-expanded={open}
        aria-controls="atlas-notification-panel"
        aria-haspopup="dialog"
      >
        <Bell className="w-5 h-5" />
        <AnimatePresence>
          {unread > 0 ? (
            <motion.span
              key="badge"
              initial={{ scale: 0.6, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.6, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 420, damping: 22 }}
              className="absolute -top-1.5 -right-1.5 min-w-[1.25rem] h-5 px-1 rounded-full bg-[#EF4444] text-white text-[10px] font-bold flex items-center justify-center shadow-sm"
            >
              {unread > 99 ? '99+' : unread}
            </motion.span>
          ) : null}
        </AnimatePresence>
      </button>

      <AnimatePresence>
        {open ? (
          <motion.div
            id="atlas-notification-panel"
            role="dialog"
            aria-label="Notifications"
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.16 }}
            className="absolute right-0 mt-2 w-[min(100vw-2rem,22rem)] max-h-[min(70vh,28rem)] overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white shadow-xl shadow-[#0F172A]/10"
          >
            <div className="flex items-center justify-between gap-2 px-4 py-3 border-b border-slate-100 bg-gradient-to-r from-[#EFF6FF] to-white">
              <div>
                <p className="text-sm font-semibold text-[#0F172A]">Notifications</p>
                <p className="text-[11px] text-[#64748B]">
                  {unread > 0 ? `${unread} unread` : 'You are up to date'}
                </p>
              </div>
              {unread > 0 ? (
                <button
                  type="button"
                  onClick={() => void onMarkAll()}
                  className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#2563EB] hover:text-[#1D4ED8]"
                >
                  <CheckCheck className="w-3.5 h-3.5" />
                  Mark all read
                </button>
              ) : null}
            </div>

            <div className="overflow-y-auto max-h-[min(58vh,22rem)]">
              {loading && items.length === 0 ? (
                <div className="flex items-center justify-center gap-2 py-10 text-sm text-slate-400">
                  <Loader2 className="w-4 h-4 animate-spin" /> Loading…
                </div>
              ) : items.length === 0 ? (
                <div className="px-5 py-10 text-center">
                  <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-[#EFF6FF] text-[#2563EB]">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <p className="text-sm font-medium text-slate-800">No notifications yet</p>
                  <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">
                    As you complete challenges, phases and learning activities, your
                    notifications will appear here.
                  </p>
                </div>
              ) : (
                <ul className="divide-y divide-slate-100">
                  {items.map((item) => {
                    const meta = typeMeta(item.category || item.type);
                    const Icon = meta.icon;
                    const unreadRow = isUnread(item);
                    const href = actionHref(item);
                    return (
                      <li key={item.id}>
                        <button
                          type="button"
                          onClick={() => void onOpenItem(item)}
                          className={`w-full text-left px-4 py-3.5 flex gap-3 transition-colors ${
                            unreadRow
                              ? 'bg-[#EFF6FF]/80 hover:bg-[#DBEAFE]'
                              : 'bg-white hover:bg-slate-50'
                          }`}
                        >
                          <div
                            className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${meta.iconWrap}`}
                          >
                            <Icon className="w-4 h-4" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-start justify-between gap-2">
                              <p
                                className={`text-sm leading-snug ${
                                  unreadRow
                                    ? 'font-semibold text-[#0F172A]'
                                    : 'font-medium text-slate-700'
                                }`}
                              >
                                {item.title}
                              </p>
                              {unreadRow ? (
                                <span
                                  className="mt-1 h-2 w-2 shrink-0 rounded-full bg-[#2563EB]"
                                  aria-label="Unread"
                                />
                              ) : null}
                            </div>
                            <p className="mt-0.5 text-xs text-slate-500 leading-relaxed line-clamp-2">
                              {item.message}
                            </p>
                            <div className="mt-1.5 flex items-center gap-2">
                              <span
                                className={`rounded-md px-1.5 py-0.5 text-[10px] font-semibold ${meta.chip}`}
                              >
                                {meta.label}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                {formatWhen(item.created_at)}
                              </span>
                              {href ? (
                                <span className="ml-auto inline-flex items-center gap-0.5 text-[10px] font-semibold text-[#2563EB]">
                                  Open
                                  <ChevronRight className="w-3 h-3" />
                                </span>
                              ) : null}
                            </div>
                          </div>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
