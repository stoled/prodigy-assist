"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = require("fs");
const path_1 = require("path");
const dotenv_1 = require("dotenv");
const dotenv_expand_1 = require("dotenv-expand");
const envCandidates = [
    (0, path_1.resolve)(process.cwd(), '.env'),
    (0, path_1.resolve)(process.cwd(), '../.env'),
];
for (const envPath of envCandidates) {
    if ((0, fs_1.existsSync)(envPath)) {
        const loaded = (0, dotenv_1.config)({ path: envPath, override: false });
        (0, dotenv_expand_1.expand)(loaded);
    }
}
//# sourceMappingURL=load-root-env.js.map