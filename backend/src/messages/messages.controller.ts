import {
  Controller,
  Post,
  Get,
  Delete,
  Param,
  Body,
  Query,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { MessagesService } from './messages.service';
import { SendMessageDto } from './dto/send-message.dto';

@Controller('messages')
export class MessagesController {
  constructor(private readonly messagesService: MessagesService) {}

  // POST /messages — accept a message from the bot and return a reply
  @Post()
  @HttpCode(HttpStatus.OK)
  send(@Body() dto: SendMessageDto) {
    return this.messagesService.send(dto);
  }

  // GET /messages/:telegramId — conversation history
  @Get(':telegramId')
  getHistory(
    @Param('telegramId') telegramId: string,
    @Query('limit') limit?: string,
    @Query('offset') offset?: string,
  ) {
    return this.messagesService.getHistory(
      telegramId,
      limit ? parseInt(limit, 10) : undefined,
      offset ? parseInt(offset, 10) : undefined,
    );
  }

  // DELETE /messages/:telegramId — delete history
  @Delete(':telegramId')
  deleteHistory(@Param('telegramId') telegramId: string) {
    return this.messagesService.deleteHistory(telegramId);
  }
}
