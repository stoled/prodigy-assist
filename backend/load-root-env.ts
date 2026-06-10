import { existsSync } from 'fs';
import { resolve } from 'path';
import { config as loadEnv } from 'dotenv';
import { expand } from 'dotenv-expand';

const envCandidates = [
  resolve(process.cwd(), '.env'),
  resolve(process.cwd(), '../.env'),
];

for (const envPath of envCandidates) {
  if (existsSync(envPath)) {
    const loaded = loadEnv({ path: envPath, override: false });
    expand(loaded);
  }
}
