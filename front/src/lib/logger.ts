import pino from "pino";

/** Log level: trace | debug | info | warn | error | fatal. Set VITE_LOG_LEVEL in .env (Vite env). */
// const level = import.meta.env.VITE_LOG_LEVEL ?? "info";

// export const logger = pino({ level });
export const logger = pino({ level: "error" });