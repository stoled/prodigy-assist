export const config = {
  telegramToken: process.env.TELEGRAM_TOKEN,
  backendUrl: process.env.BACKEND_URL ?? 'http://backend:3000',
} as const;

if (!config.telegramToken) {
  throw new Error('TELEGRAM_TOKEN is not set');
}
