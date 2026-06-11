import { Telegraf } from 'telegraf';
import { config } from './config.js';
import { BackendAPI } from './api.js';
import { BotHandlers } from './handlers.js';
import { logger } from './logger.js';
import { message } from 'telegraf/filters';

const bot = new Telegraf(config.telegramToken!);
const api = new BackendAPI();
const handlers = new BotHandlers(api);

bot.start((ctx) => handlers.handleStart(ctx));
bot.on(message('text'), (ctx) => handlers.handleText(ctx));

bot.launch();
logger.info('Telegram bot started');

process.once('SIGINT', () => {
  logger.info('Received SIGINT, stopping bot');
  bot.stop('SIGINT');
});

process.once('SIGTERM', () => {
  logger.info('Received SIGTERM, stopping bot');
  bot.stop('SIGTERM');
});
