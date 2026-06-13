import {
  Injectable,
  Logger,
  NotFoundException,
  ServiceUnavailableException,
} from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import { CreateKnowledgeDto } from './dto/create-knowledge.dto';

@Injectable()
export class KnowledgeService {
  private readonly logger = new Logger(KnowledgeService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {}

  async create(dto: CreateKnowledgeDto) {
    // 1. Сохранить документ в PostgreSQL
    const document = await this.prisma.document.create({
      data: {
        title: dto.title,
        content: dto.content,
        source: dto.source ?? 'manual',
        lang: dto.lang ?? 'en',
      },
    });

    // 2. Отправить на индексацию в AI Service
    const aiServiceUrl = this.configService.get<string>('AI_SERVICE_URL');

    try {
      await this.httpService.axiosRef.post(`${aiServiceUrl}/embeddings`, {
        document_id: document.id,
        title: document.title,
        content: document.content,
      });
    } catch (error) {
      this.logger.error('Failed to index document in AI Service', {
        documentId: document.id,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw new ServiceUnavailableException(
        'Document saved but indexing failed. Please try again later.',
      );
    }

    return {
      id: document.id,
      title: document.title,
      source: document.source,
      status: 'indexed',
    };
  }

  async search(query: string) {
    const aiServiceUrl = this.configService.get<string>('AI_SERVICE_URL');

    try {
      const { data } = await this.httpService.axiosRef.get(
        `${aiServiceUrl}/search`,
        { params: { q: query } },
      );
      return data;
    } catch (error) {
      this.logger.error('Failed to search knowledge', { query, error });
      throw new ServiceUnavailableException('Search service unavailable.');
    }
  }

  async delete(id: string) {
    const document = await this.prisma.document.findUnique({ where: { id } });

    if (!document) {
      throw new NotFoundException(`Document ${id} not found`);
    }

    // Чанки удалятся каскадно (onDelete: Cascade)
    await this.prisma.document.delete({ where: { id } });

    return { success: true };
  }
}
