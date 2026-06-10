import { PrismaService } from '../prisma/prisma.service';
import { CreateUserDto } from './dto/create-user.dto';
export declare class UsersService {
    private readonly prisma;
    constructor(prisma: PrismaService);
    findOrCreate(dto: CreateUserDto): Promise<{
        telegramId: string;
        id: string;
        createdAt: Date;
    }>;
    findByTelegramId(telegramId: string): Promise<{
        telegramId: string;
        id: string;
        createdAt: Date;
    }>;
}
