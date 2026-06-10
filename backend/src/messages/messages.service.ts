import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { firstValueFrom } from 'rxjs';
import { PrismaService } from '../prisma/prisma.service';
import { UsersService } from '../users/users.service';
import { SendMessageDto } from './dto/send-message.dto';

@Injectable()
export class MessagesService {
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

    // 3. Запросить ответ у AI Service
    const aiServiceUrl = this.configService.get<string>('AI_SERVICE_URL');
    const { data } = await firstValueFrom(
      this.httpService.post<{ reply: string }>(`${aiServiceUrl}/generate`, {
        message: dto.text,
      }),
    );

    // 4. Сохранить ответ ассистента
    await this.prisma.message.create({
      data: {
        role: 'assistant',
        content: data.reply,
        userId: user.id,
      },
    });

    return { reply: data.reply };
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
