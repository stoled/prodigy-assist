import axios from 'axios';
import { config } from './config.js';

export interface SendMessageRequest {
  telegramId: string;
  text: string;
}

export interface SendMessageResponse {
  reply: string;
}

export class BackendAPI {
  private readonly baseUrl: string;

  constructor(baseUrl: string = config.backendUrl) {
    this.baseUrl = baseUrl;
  }

  async sendMessage(
    telegramId: string,
    text: string,
  ): Promise<SendMessageResponse> {
    const { data } = await axios.post<SendMessageResponse>(
      `${this.baseUrl}/messages`,
      { telegramId, text },
    );
    return data;
  }
}
