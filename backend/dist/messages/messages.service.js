"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MessagesService = void 0;
const common_1 = require("@nestjs/common");
const axios_1 = require("@nestjs/axios");
const config_1 = require("@nestjs/config");
const rxjs_1 = require("rxjs");
const prisma_service_1 = require("../prisma/prisma.service");
const users_service_1 = require("../users/users.service");
let MessagesService = class MessagesService {
    prisma;
    usersService;
    httpService;
    configService;
    constructor(prisma, usersService, httpService, configService) {
        this.prisma = prisma;
        this.usersService = usersService;
        this.httpService = httpService;
        this.configService = configService;
    }
    async send(dto) {
        const user = await this.usersService.findOrCreate({
            telegramId: dto.telegramId,
        });
        await this.prisma.message.create({
            data: {
                role: 'user',
                content: dto.text,
                userId: user.id,
            },
        });
        const aiServiceUrl = this.configService.get('AI_SERVICE_URL');
        const { data } = await (0, rxjs_1.firstValueFrom)(this.httpService.post(`${aiServiceUrl}/generate`, {
            message: dto.text,
        }));
        await this.prisma.message.create({
            data: {
                role: 'assistant',
                content: data.reply,
                userId: user.id,
            },
        });
        return { reply: data.reply };
    }
    async getHistory(telegramId) {
        const user = await this.usersService.findByTelegramId(telegramId);
        return this.prisma.message.findMany({
            where: { userId: user.id },
            orderBy: { createdAt: 'asc' },
        });
    }
    async deleteHistory(telegramId) {
        const user = await this.usersService.findByTelegramId(telegramId);
        await this.prisma.message.deleteMany({ where: { userId: user.id } });
        return { success: true };
    }
};
exports.MessagesService = MessagesService;
exports.MessagesService = MessagesService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_service_1.PrismaService,
        users_service_1.UsersService,
        axios_1.HttpService,
        config_1.ConfigService])
], MessagesService);
//# sourceMappingURL=messages.service.js.map