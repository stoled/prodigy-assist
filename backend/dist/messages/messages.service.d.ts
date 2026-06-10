import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import { UsersService } from '../users/users.service';
import { SendMessageDto } from './dto/send-message.dto';
export declare class MessagesService {
    private readonly prisma;
    private readonly usersService;
    private readonly httpService;
    private readonly configService;
    constructor(prisma: PrismaService, usersService: UsersService, httpService: HttpService, configService: ConfigService);
    send(dto: SendMessageDto): Promise<{
        reply: string;
    }>;
    getHistory(telegramId: string): Promise<{
        id: string;
        createdAt: Date;
        role: string;
        content: string;
        userId: string;
    }[]>;
    deleteHistory(telegramId: string): Promise<{
        success: boolean;
    }>;
}
