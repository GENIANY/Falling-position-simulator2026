/** Lifecycle of the existing screen controllers. React owns the host, each
 * controller owns its descendants; only dedicated portals belong to React. */
export function screenScope(host: HTMLElement, initial: Record<string, unknown> = {}) {
  const listeners: (() => void)[] = [], timers = new Set<number>(), frames = new Set<number>();
  const observers: { disconnect(): void }[] = [];
  let alive = true;
  const local: Record<string, unknown> = {...initial};
  const listen = (target: EventTarget, type: string, fn: EventListenerOrEventListenerObject, options?: AddEventListenerOptions | boolean) => {
    target.addEventListener(type, fn, options);
    listeners.push(() => target.removeEventListener(type, fn, options));
  };
  const setTimer = (fn: (...args: unknown[]) => void, ms?: number, ...args: unknown[]) => {
    const id = window.setTimeout(() => { timers.delete(id); if (alive) fn(...args); }, ms); timers.add(id); return id;
  };
  const frame = (fn: FrameRequestCallback) => { const id = requestAnimationFrame(t => { frames.delete(id); if (alive) fn(t); }); frames.add(id); return id; };
  const scopedDocument = new Proxy(document, {
    get(target, key) {
      if (key === 'body' || key === 'documentElement') return host;
      if (key === 'getElementById') return (id: string) => host.querySelector('#' + CSS.escape(id)) ?? document.getElementById(id);
      if (key === 'querySelector') return (selector: string) => host.querySelector(selector);
      if (key === 'querySelectorAll') return (selector: string) => host.querySelectorAll(selector);
      if (key === 'addEventListener') return (type: string, fn: EventListener, options?: boolean) => listen(document, type, fn, options);
      const value = Reflect.get(target, key, target); return typeof value === 'function' ? value.bind(target) : value;
    }
  });
  class ScopedMutationObserver extends MutationObserver { constructor(fn: MutationCallback) { super(fn); observers.push(this); } }
  class ScopedResizeObserver extends ResizeObserver { constructor(fn: ResizeObserverCallback) { super(fn); observers.push(this); } }
  const scopedWindow = new Proxy(window, {
    get(target, key) {
      if (key in local) return local[key as string];
      if (key === 'document') return scopedDocument;
      if (key === 'setTimeout') return setTimer;
      if (key === 'requestAnimationFrame') return frame;
      if (key === 'addEventListener') return (type: string, fn: EventListener, options?: boolean) => listen(window, type, fn, options);
      const value = Reflect.get(target, key, target); return typeof value === 'function' && !String(key).match(/^[A-Z]/) ? value.bind(target) : value;
    },
    set(_target, key, value) { local[key as string] = value; return true; }
  });
  return {host, window: scopedWindow, document: scopedDocument, local,
    setTimeout: setTimer, clearTimeout: window.clearTimeout.bind(window),
    requestAnimationFrame: frame, cancelAnimationFrame: window.cancelAnimationFrame.bind(window),
    addEventListener: (type: string, fn: EventListener, options?: boolean) => listen(window, type, fn, options),
    MutationObserver: ScopedMutationObserver, ResizeObserver: ScopedResizeObserver,
    dispose() { alive = false; listeners.forEach(fn => fn()); timers.forEach(clearTimeout); frames.forEach(cancelAnimationFrame); observers.forEach(o => o.disconnect()); }
  };
}
