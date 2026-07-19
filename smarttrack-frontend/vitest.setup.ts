import '@testing-library/jest-dom/vitest';

/**
 * Node 20+/22 can expose a broken global localStorage stub that lacks
 * getItem/setItem/removeItem/clear. Replace it with a minimal in-memory
 * Storage implementation for auth session tests.
 */
class MemoryStorage implements Storage {
  private store = new Map<string, string>();

  get length(): number {
    return this.store.size;
  }

  clear(): void {
    this.store.clear();
  }

  getItem(key: string): string | null {
    return this.store.has(key) ? this.store.get(key)! : null;
  }

  key(index: number): string | null {
    return Array.from(this.store.keys())[index] ?? null;
  }

  removeItem(key: string): void {
    this.store.delete(key);
  }

  setItem(key: string, value: string): void {
    this.store.set(String(key), String(value));
  }
}

const local = new MemoryStorage();
const session = new MemoryStorage();

Object.defineProperty(globalThis, 'localStorage', {
  configurable: true,
  value: local,
});
Object.defineProperty(globalThis, 'sessionStorage', {
  configurable: true,
  value: session,
});

if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'localStorage', {
    configurable: true,
    value: local,
  });
  Object.defineProperty(window, 'sessionStorage', {
    configurable: true,
    value: session,
  });
}
