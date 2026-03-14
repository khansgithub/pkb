/**
 * Parses create_db.sql for schema types and queries.sql for -- @param, -- @returns, -- @from.
 * Generates TypeScript types for schema, query parameters, and row types.
 * Run: npm run generate:sql-types
 */
import { readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const createDbPath = join(__dirname, '..', 'src', 'sql', 'create_db.sql');
const sqlPath = join(__dirname, '..', 'src', 'sql', 'queries.sql');
const outPath = join(__dirname, '..', 'src', 'sql', 'sql-types.generated.ts');

const createDbRaw = readFileSync(createDbPath, 'utf-8');
const raw = readFileSync(sqlPath, 'utf-8');

/** Maps SQL type strings to TypeScript types */
const sqlToTsType: Record<string, string> = {
  serial: 'number',
  integer: 'number',
  int: 'number',
  smallint: 'number',
  bigint: 'number',
  text: 'string',
  varchar: 'string',
  char: 'string',
  timestamptz: 'string',
  timestamp: 'string',
  date: 'string',
  'text[]': 'string[]',
  'text[][]': 'string[][]',
};

function sqlTypeToTs(sqlType: string, nullable: boolean): string {
  const base = sqlToTsType[sqlType.toLowerCase()] ?? 'unknown';
  return nullable ? `${base} | null` : base;
}

function toPascalCase(s: string): string {
  return s
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join('');
}

/** Parse CREATE TABLE from create_db.sql and generate schema types */
const createTableBlocks = [
  ...createDbRaw.matchAll(/create\s+table\s+(\w+)\s*\(([\s\S]*?)\)\s*;/gi),
];

const schemaTypes: string[] = [];
const tableToSchema: Record<string, string> = {};

for (const [, tableName, body] of createTableBlocks) {
  const tsName = toPascalCase(tableName!) + 'Row';
  tableToSchema[tableName!.toLowerCase()] = tsName;

  const columnParts = body!
    .replace(/--[^\n]*/g, '')
    .split(',')
    .map((p) => p.trim())
    .filter((p) => p && !p.toLowerCase().startsWith('constraint'));

  const fields: string[] = [];
  for (const part of columnParts) {
    const colMatch = part.match(/^(\w+)\s+(\w+(?:\[\])?)(?:\s+(.*))?$/i);
    if (!colMatch) continue;
    const [, colName, sqlType, rest = ''] = colMatch;
    const restLower = rest.toLowerCase();
    const nullable = !restLower.includes('not null') && !restLower.includes('primary key');
    const tsType = sqlTypeToTs(sqlType!, nullable);
    fields.push(`  ${colName}: ${tsType};`);
  }
  if (fields.length > 0) {
    schemaTypes.push(`export type ${tsName} = {\n${fields.join('\n')}\n};`);
  }
}

const typeMap: Record<string, string> = {
  string: 'string',
  number: 'number',
  boolean: 'boolean',
  'string | null': 'string | null',
  'number | null': 'number | null',
  'boolean | null': 'boolean | null',
  'string[]': 'string[]',
  'string[][]': 'string[][]',
};

const queryBlocks = [...raw.matchAll(/-- query:(\w+)\s*[\r\n]+([\s\S]*?)[\r\n]+\s*-- end/g)];

const queryParamMap: Record<string, string> = {};
const queryRowMap: Record<string, string> = {};

for (const [, name, block] of queryBlocks) {
  const paramLines = [...block.matchAll(/--\s*@param\s+\$(\d+):\s*([\w\s|]+?)(?:\s+-\s+(.*))?$/gm)];
  const params = paramLines
    .map(([, pos, type, desc]) => ({
      position: parseInt(pos!, 10),
      type: (typeMap[type!.trim()] ?? type!.trim() ?? 'unknown').replace(/\s+/g, ' '),
      description: desc?.trim() ?? '',
    }))
    .sort((a, b) => a.position - b.position);

  const tsTypes = params.map((p) => p.type);
  queryParamMap[name!] = tsTypes.length > 0 ? `[${tsTypes.join(', ')}]` : '[]';

  // Parse @from and @returns for row types
  const fromMatch = block.match(/--\s*@from\s+(\w+)/);
  const returnsMatch = block.match(/--\s*@returns\s+(.+?)(?=\s*$|\s*--|\s*$)/m);
  const returnsRaw = returnsMatch?.[1]?.trim();

  if (fromMatch && returnsRaw) {
    const table = fromMatch[1];
    const schemaType = tableToSchema[table];
    if (schemaType) {
      const cols = returnsRaw.split(',').map((c) => c.trim());
      queryRowMap[name!] = `Pick<${schemaType}, ${cols.map((c) => `'${c}'`).join(' | ')}>`;
    } else {
      queryRowMap[name!] = 'Record<string, unknown>';
    }
  } else if (returnsRaw && returnsRaw.includes(':')) {
    const entries = returnsRaw.split(',').map((e) => e.trim());
    const fields = entries.map((e) => {
      const [col, type] = e.split(':').map((s) => s.trim());
      const tsType = typeMap[type] ?? type ?? 'unknown';
      return `    ${col}: ${tsType};`;
    });
    queryRowMap[name!] = `{\n${fields.join('\n')}\n  }`;
  } else if (returnsRaw) {
    const cols = returnsRaw.split(',').map((c) => c.trim());
    if (cols.length === 1 && cols[0] === 'set_limit') {
      queryRowMap[name!] = '{ set_limit: number }';
    } else {
      queryRowMap[name!] = `{ ${cols.map((c) => `${c}: unknown`).join('; ')} }`;
    }
  } else {
    queryRowMap[name!] = 'Record<string, unknown>';
  }
}

const lines = [
  '/** Auto-generated from create_db.sql and queries.sql - do not edit manually. Run: npm run generate:sql-types */',
  '',
  '// --- Schema types (from create_db.sql) ---',
  '',
  ...schemaTypes,
  '',
  '// --- Query param and row types (from queries.sql) ---',
  '',
  'export type QueryParamMap = {',
  ...Object.entries(queryParamMap).map(([k, v]) => `  ${k}: ${v};`),
  '};',
  '',
  'export type QueryName = keyof QueryParamMap;',
  '',
  'export type QueryRowMap = {',
  ...Object.entries(queryRowMap).map(([k, v]) => `  ${k}: ${v};`),
  '};',
  '',
  '/** Row type for a specific query. Use with db.query(sql, params) result. */',
  'export type QueryRow<K extends QueryName> = QueryRowMap[K];',
  '',
  '// --- Row type aliases (one per query) ---',
  '',
  ...Object.keys(queryRowMap).flatMap((name) => [
    `/** Row type for ${name} query */`,
    `export type ${toPascalCase(name) + 'Row'} = QueryRowMap['${name}'];`,
    '',
  ]),
];

writeFileSync(outPath, lines.join('\n'), 'utf-8');
console.log('Generated', outPath);
