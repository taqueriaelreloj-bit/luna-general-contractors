import { readFileSync } from 'node:fs';

export default JSON.parse(readFileSync(new URL('./cloud-approved-images.json', import.meta.url), 'utf8'));
