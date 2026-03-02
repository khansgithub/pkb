import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const raw = readFileSync(join(__dirname, 'sql', 'queries.sql'), 'utf-8');
const queries: Record<string, string> = {};
for (const block of raw.matchAll(/-- query:(\w+)\s*[\r\n]+([\s\S]*?)[\r\n]+\s*-- end/g)) {
  queries[block[1]] = block[2].trim();
}

export function getQuery(name: string): string {
  const sql = queries[name];
  if (!sql) throw new Error(`Unknown query: ${name}. Available: ${Object.keys(queries).join(', ')}`);
  return sql;
}
