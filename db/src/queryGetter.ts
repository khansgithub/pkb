import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import type { QueryName, QueryParamMap } from './sql/sql-types.generated';


export type { QueryName, QueryParamMap };

const __dirname = dirname(fileURLToPath(import.meta.url));

export interface ParamInfo {
  position: number;
  type: string;
  description: string;
}

export interface QueryResult<K extends QueryName> {
  sql: string;
  /** Documented parameters for this query - use with db.query(sql, params) */
  paramInfo: ParamInfo[];
  /** Type hint for params - use `params: QueryParamMap[K]` when calling db.query(sql, params) */
  readonly _params?: QueryParamMap[K];
}

const raw = readFileSync(join(__dirname, 'sql', 'queries.sql'), 'utf-8');

const queryBlocks: Array<{ name: string; sql: string; paramInfo: ParamInfo[] }> = [];

for (const block of raw.matchAll(/-- query:(\w+)\s*[\r\n]+([\s\S]*?)[\r\n]+\s*-- end/g)) {
  const name = block[1];
  const content = block[2];
  if (!content || !name) throw new Error("unexpected error");

  const paramLines = [...content.matchAll(/--\s*@param\s+\$(\d+):\s*([\w\s|]+?)(?:\s+-\s+(.*))?$/gm)];
  const paramInfo: ParamInfo[] = paramLines
    .map(([, pos, type, desc]) => ({
      position: parseInt(pos!, 10),
      type: type!.trim(),
      description: desc?.trim() ?? '',
    }))
    .sort((a, b) => a.position - b.position);

  const sql = content.replace(/--\s*@param\s+\$\d+:[^\r\n]*[\r\n]*/gm, '').trim();

  queryBlocks.push({ name, sql, paramInfo });
}

const queries = Object.fromEntries(queryBlocks.map((q) => [q.name, q]));

export function getQuery<K extends QueryName>(name: K): QueryResult<K> {
  const q = queries[name];
  if (!q)
    throw new Error(`Unknown query: ${name}. Available: ${Object.keys(queries).join(', ')}`);
  return { sql: q.sql, paramInfo: q.paramInfo } as QueryResult<K>;
}
