import { Telegraf } from 'telegraf';
import axios from 'axios';
const token = process.env.TELEGRAM_TOKEN;
const backendUrl = process.env.BACKEND_URL ?? 'http://backend:3000';
if (!token) {
    throw new Error('TELEGRAM_TOKEN is not set');
}
const bot = new Telegraf(token);
bot.start((ctx) => {
    ctx.reply('Привет! Я бот-всезнайка. Задавай любые вопросы!');
});
bot.on('text', async (ctx) => {
    const telegramId = String(ctx.from.id);
    const text = ctx.message.text;
    try {
        await ctx.sendChatAction('typing');
        const { data } = await axios.post(`${backendUrl}/messages`, { telegramId, text });
        await ctx.reply(data.reply);
    }
    catch (err) {
        console.error('Error calling backend:', err);
        await ctx.reply('Произошла ошибка. Попробуй ещё раз.');
    }
});
bot.launch();
console.log('Telegram bot started');
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
//# sourceMappingURL=index.js.map