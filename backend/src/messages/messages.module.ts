import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { MessagesController } from './messages.controller';
import { MessagesService } from './messages.service';
import { UsersModule } from '../users/users.module';

@Module({
  imports: [HttpModule, UsersModule],
  controllers: [MessagesController],
  providers: [MessagesService],
})
export class MessagesModule {}
