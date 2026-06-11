type LogLevel = 'info' | 'error';

class Logger {
  private log(level: LogLevel, message: string, meta?: Record<string, unknown>): void {
    const timestamp = new Date().toISOString();
    const logData = {
      timestamp,
      level,
      message,
      ...(meta && { meta }),
    };
    console.log(JSON.stringify(logData));
  }

  info(message: string, meta?: Record<string, unknown>): void {
    this.log('info', message, meta);
  }

  error(message: string, meta?: Record<string, unknown>): void {
    this.log('error', message, meta);
  }
}

export const logger = new Logger();
