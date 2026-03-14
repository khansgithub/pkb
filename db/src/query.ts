import type { PGlite } from '@electric-sql/pglite';
import { getQuery, type QueryParamMap } from './queryGetter';
import type { CodeblocksFtsRow, CodeblocksTrigramRow, SnippetsTrigramRow } from './sql/sql-types.generated';


export async function codeblocksFtsQuery(db: PGlite, params: QueryParamMap['codeblocks_fts']): Promise<CodeblocksFtsRow[]> {
    const query = getQuery("codeblocks_fts");
    const { rows }: { rows: CodeblocksFtsRow[] } = await db.query(query.sql, params);
    return rows;
}

export async function codeblocksTrigramQuery(db: PGlite, params: QueryParamMap['codeblocks_trigram']): Promise<CodeblocksTrigramRow[]> {
    const query = getQuery("codeblocks_trigram");
    const { rows }: { rows: CodeblocksTrigramRow[] } = await db.query(query.sql, params);
    return rows;
}

export async function snippetsTrigramQuery(db: PGlite, params: QueryParamMap['snippets_trigram']): Promise<SnippetsTrigramRow[]> {
    const query = getQuery("snippets_trigram");
    const { rows }: { rows: SnippetsTrigramRow[] } = await db.query(query.sql, params);
    return rows;
}

export async function snippetsFtsQuery(db: PGlite, params: QueryParamMap['snippets_fts']): Promise<SnippetsTrigramRow[]> {
    const query = getQuery("snippets_fts");
    const { rows }: { rows: SnippetsTrigramRow[] } = await db.query(query.sql, params);
    return rows;
}