import { MessagesService } from './messages.service';
import { SendMessageDto } from './dto/send-message.dto';
export declare class MessagesController {
    private readonly messagesService;
    constructor(messagesService: MessagesService);
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
