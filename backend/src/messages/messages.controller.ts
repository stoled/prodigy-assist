import {
  Controller,
  Post,
  Get,
  Delete,
  Param,
  Body,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { MessagesService } from './messages.service';
import { SendMessageDto } from './dto/send-message.dto';

@Controller('messages')
export class MessagesController {
  constructor(private readonly messagesService: MessagesService) {}

  // POST /messages — принять сообщение от бота и вернуть ответ
  @Post()
  @HttpCode(HttpStatus.OK)
  send(@Body() dto: SendMessageDto) {
    return this.messagesService.send(dto);
  }

  // GET /messages/:telegramId — история диалога
  @Get(':telegramId')
  getHistory(@Param('telegramId') telegramId: string) {
    return this.messagesService.getHistory(telegramId);
  }

  // DELETE /messages/:telegramId — удалить историю
  @Delete(':telegramId')
  deleteHistory(@Param('telegramId') telegramId: string) {
    return this.messagesService.deleteHistory(telegramId);
  }
}
