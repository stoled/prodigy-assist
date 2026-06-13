import { IsString, IsNotEmpty } from 'class-validator';

export class SearchKnowledgeDto {
  @IsString()
  @IsNotEmpty()
  q!: string;
}
