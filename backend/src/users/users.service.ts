import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateUserDto } from './dto/create-user.dto';

@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

  async findOrCreate(dto: CreateUserDto) {
    return this.prisma.user.upsert({
      where: { telegramId: dto.telegramId },
      update: {},
      create: { telegramId: dto.telegramId },
    });
  }

  async findByTelegramId(telegramId: string) {
    const user = await this.prisma.user.findUnique({
      where: { telegramId },
    });
    if (!user) {
      throw new NotFoundException(`User with telegramId ${telegramId} not found`);
    }
    return user;
  }
}
