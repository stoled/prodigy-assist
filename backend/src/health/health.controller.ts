import { Controller, Get } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';

@Controller('health')
export class HealthController {
  constructor(
    private readonly prisma: PrismaService,
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {}

  @Get()
  async health() {
    const checks: Record<string, string> = {};

    // Check PostgreSQL
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      checks['postgres'] = 'ok';
    } catch (e) {
      checks['postgres'] =
        `error: ${e instanceof Error ? e.message : 'unknown'}`;
    }

    // Check AI Service
    try {
      const aiServiceUrl = this.configService.get<string>('AI_SERVICE_URL');
      await this.httpService.axiosRef.get(`${aiServiceUrl}/health`, {
        timeout: 3000,
      });
      checks['ai-service'] = 'ok';
    } catch (e) {
      checks['ai-service'] =
        `error: ${e instanceof Error ? e.message : 'unknown'}`;
    }

    const overall = Object.values(checks).every((v) => v === 'ok')
      ? 'ok'
      : 'degraded';

    return { status: overall, checks };
  }
}
