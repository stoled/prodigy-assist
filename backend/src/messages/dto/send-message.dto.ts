import { IsString, IsNotEmpty } from 'class-validator';

export class SendMessageDto {
  @IsString()
  @IsNotEmpty()
  telegramId: string;

  @IsString()
  @IsNotEmpty()
  text: string;
}
