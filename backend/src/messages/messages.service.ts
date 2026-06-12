import {
  Injectable,
  ServiceUnavailableException,
  Logger,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { AxiosError } from 'axios';
import { PrismaService } from '../prisma/prisma.service';
import { UsersService } from '../users/users.service';
import { SendMessageDto } from './dto/send-message.dto';

@Injectable()
export class MessagesService {
  private readonly logger = new Logger(MessagesService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly usersService: UsersService,
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {}

  async send(dto: SendMessageDto): Promise<{ reply: string }> {
    // 1. Найти или создать пользователя
    const user = await this.usersService.findOrCreate({
      telegramId: dto.telegramId,
    });

    // 2. Сохранить сообщение пользователя (вопрос)
    const userMessage = await this.prisma.message.create({
      data: {
        role: 'user',
        content: dto.text,
        userId: user.id,
        parentId: null,
      },
    });

    // 3. Запросить ответ у AI Service с retry логикой
    const aiServiceUrl = this.configService.get<string>('AI_SERVICE_URL');
    let reply: string;

    try {
      reply = await this.callAiServiceWithRetry(
        aiServiceUrl!,
        dto.text,
        dto.telegramId,
      );
    } catch (error) {
      this.logger.error('Failed to get AI response after retries', {
        telegramId: dto.telegramId,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw new ServiceUnavailableException(
        'AI service temporarily unavailable. Please try again later.',
      );
    }

    // 4. Сохранить ответ ассистента (связать с вопросом)
    await this.prisma.message.create({
      data: {
        role: 'assistant',
        content: reply,
        userId: user.id,
        parentId: userMessage.id,
      },
    });

    return { reply };
  }

  private async callAiServiceWithRetry(
    url: string,
    message: string,
    telegramId: string,
    maxRetries = 2,
  ): Promise<string> {
    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const { data } = await this.httpService.axiosRef.post<{
          reply: string;
        }>(`${url}/generate`, { message }, { timeout: 30000 });
        return data.reply;
      } catch (error) {
        lastError = error as Error;
        const axiosError = error as AxiosError;

        this.logger.warn(
          `AI Service call failed (attempt ${attempt + 1}/${maxRetries + 1})`,
          {
            telegramId,
            error: axiosError.message,
            status: axiosError.response?.status,
            url,
          },
        );

        // Если это последняя попытка, не ждём
        if (attempt < maxRetries) {
          await this.delay(1000);
        }
      }
    }

    throw lastError || new Error('AI Service unavailable');
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async getHistory(telegramId: string, limit = 50, offset = 0) {
    const user = await this.usersService.findByTelegramId(telegramId);

    const questions = await this.prisma.message.findMany({
      where: {
        userId: user.id,
        parentId: null,
      },
      include: {
        replies: {
          orderBy: { createdAt: 'asc' },
        },
      },
      orderBy: { createdAt: 'desc' },
      skip: offset,
      take: limit,
    });

    const total = await this.prisma.message.count({
      where: { userId: user.id, parentId: null },
    });

    return {
      data: questions,
      pagination: {
        total,
        limit,
        offset,
        hasMore: offset + limit < total,
      },
    };
  }

  async deleteHistory(telegramId: string) {
    const user = await this.usersService.findByTelegramId(telegramId);
    await this.prisma.message.deleteMany({ where: { userId: user.id } });
    return { success: true };
  }
}
