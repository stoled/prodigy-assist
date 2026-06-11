import { Context } from 'telegraf';
import { BackendAPI } from './api.js';
import { logger } from './logger.js';

export class BotHandlers {
  constructor(private readonly api: BackendAPI) {}

  async handleStart(ctx: Context): Promise<void> {
    await ctx.reply('Привет! Я бот-всезнайка. Задавай любые вопросы!');
  }

  async handleText(ctx: Context): Promise<void> {
    if (!ctx.from || !('text' in ctx.message!)) {
      return;
    }

    const telegramId = String(ctx.from.id);
    const text = ctx.message.text;

    try {
      await ctx.sendChatAction('typing');

      const response = await this.api.sendMessage(telegramId, text);

      await ctx.reply(response.reply);
    } catch (err) {
      logger.error('Error calling backend', { telegramId, error: err });
      await ctx.reply('Произошла ошибка. Попробуй ещё раз.');
    }
  }
}
