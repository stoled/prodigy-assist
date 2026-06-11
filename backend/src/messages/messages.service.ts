import { Injectable, ServiceUnavailableException, Logger } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { firstValueFrom, retry, timeout, catchError } from 'rxjs';
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

    // 2. Сохранить сообщение пользователя
    await this.prisma.message.create({
      data: {
        role: 'user',
        content: dto.text,
        userId: user.id,
      },
    });

    // 3. Запросить ответ у AI Service с обработкой ошибок
    const aiServiceUrl = this.configService.get<string>('AI_SERVICE_URL');
    
    let reply: string;
    try {
      const { data } = await firstValueFrom(
        this.httpService.post<{ reply: string }>(
          `${aiServiceUrl}/generate`,
          { message: dto.text },
          { timeout: 30000 } // 30 секунд
        ).pipe(
          timeout(30000),
          retry({
            count: 2,
            delay: 1000,
          }),
          catchError((error) => {
            this.logger.error('AI Service error', {
              telegramId: dto.telegramId,
              error: error.message,
              url: aiServiceUrl,
            });
            throw new ServiceUnavailableException(
              'AI service temporarily unavailable. Please try again later.'
            );
          })
        )
      );
      reply = data.reply;
    } catch (error) {
      // Если ошибка уже ServiceUnavailableException, пробрасываем её
      if (error instanceof ServiceUnavailableException) {
        throw error;
      }
      
      this.logger.error('Unexpected error calling AI Service', {
        telegramId: dto.telegramId,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw new ServiceUnavailableException(
        'AI service temporarily unavailable. Please try again later.'
      );
    }

    // 4. Сохранить ответ ассистента
    await this.prisma.message.create({
      data: {
        role: 'assistant',
        content: reply,
        userId: user.id,
      },
    });

    return { reply };
  }

  async getHistory(telegramId: string) {
    const user = await this.usersService.findByTelegramId(telegramId);
    return this.prisma.message.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'asc' },
    });
  }

  async deleteHistory(telegramId: string) {
    const user = await this.usersService.findByTelegramId(telegramId);
    await this.prisma.message.deleteMany({ where: { userId: user.id } });
    return { success: true };
  }
}
