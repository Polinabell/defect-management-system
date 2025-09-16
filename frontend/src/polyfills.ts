// Minimal polyfills for CRA v4 + Node >=20 in browser
// Provide process.env and Buffer where referenced by old deps

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const g: any = (typeof globalThis !== 'undefined' ? globalThis : window) as any;

if (!g.process) {
  g.process = { env: {} };
}
if (!g.process.env) {
  g.process.env = {};
}
// Mirror to window for libs accessing window.process
if (typeof window !== 'undefined' && !(window as any).process) {
  (window as any).process = g.process;
}

// Synchronous lightweight Buffer shim if missing
if (!g.Buffer) {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { Buffer } = require('buffer');
    g.Buffer = Buffer;
  } catch {
    // ignore
  }
}

// Make this file a module
export {};
