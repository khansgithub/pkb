/**
 * Search and lookup queries for gist snippets and codeblocks.
 * Uses helpers from create_db.sql: snippet_searchable_text, expand_code_hashes,
 * snippet_search_result_row.
 */

import { legacyStringsToBlocks, type Snippet } from "$lib/types";
import type { Sql } from "postgres";

type LegacySearchRow = {
	id: number;
	title: string;
	tags: string[];
	description: string | null;
	snippets: string[];
};

function snippetFromLegacyRow(row: LegacySearchRow): Snippet {
	return {
		id: row.id,
		title: row.title,
		tags: row.tags,
		description: row.description ?? undefined,
		snippets: legacyStringsToBlocks(row.id, row.snippets ?? []),
	};
}

// supabase test ---------------------------------------------------------------
import { query } from "./supabaseClient";
export async function load(searchQuery: string = "") {
    const { data, error } = await query(searchQuery);
    if (error) throw error;
    return data;
}
// -----------------------------------------------------------------------------

/**
 * Full-text search over snippet text and path (simple config).
 * @param query - Full-text search query for plainto_tsquery
 * @returns Snippet rows with snippets as Block[]
 */
export async function codeblocksFtsQuery(query: string, sql: Sql): Promise<Snippet[]> {
    const rows = await sql`
        WITH
        matched AS (
            SELECT *
            FROM gist_snippets
            WHERE to_tsvector('simple', snippet_searchable_text(text_flat, path))
                @@ plainto_tsquery('simple', ${query})
        ),
        with_code AS (
            SELECT *, expand_code_hashes(code_hash) AS code_array
            FROM matched
        )
        SELECT sr.*
        FROM with_code c
        CROSS JOIN LATERAL snippet_search_result_row(c.id, c.title, c.path, c.text, c.code_array) AS sr
        LIMIT 10;
    `;
    return (rows as unknown as LegacySearchRow[]).map(snippetFromLegacyRow);
}

/**
 * Trigram similarity search over snippet text and path.
 * @param query - Search string for trigram similarity matching
 * @returns Snippet rows with snippets as Block[]
 */
export async function codeblocksTrigramQuery(query: string, sql: Sql): Promise<Snippet[]> {
    const rows = await sql`
        WITH trigram_snippets AS (
            SELECT
                *,
                similarity(snippet_searchable_text(text_flat, path), ${query}) AS sim
            FROM gist_snippets
            WHERE snippet_searchable_text(text_flat, path) % ${query}
        ),
        with_code AS (
            SELECT ts.*, expand_code_hashes(ts.code_hash) AS code_array
            FROM trigram_snippets ts
        ),
        ordered AS (
            SELECT *, row_number() OVER (ORDER BY sim DESC) AS rn
            FROM with_code
        )
        SELECT sr.*
        FROM ordered o
        CROSS JOIN LATERAL snippet_search_result_row(o.id, o.title, o.path, o.text, o.code_array) AS sr
        ORDER BY o.rn
        LIMIT 10;
    `;
    return (rows as unknown as LegacySearchRow[]).map(snippetFromLegacyRow);
}

/**
 * Full-text search over codeblock content (english config).
 * @param query - Full-text search query for plainto_tsquery
 * @returns Snippet rows with snippets as Block[]
 */
export async function snippetsTrigramQuery(query: string, sql: Sql): Promise<Snippet[]> {
    const rows = await sql`
        WITH results AS (
            SELECT *
            FROM gist_codeblocks
            WHERE to_tsvector('english', coalesce(code_flat, '')) @@ plainto_tsquery('english', ${query})
        ),
        joined AS (
            SELECT gs.id, gs.path, gs.title, gs.text, gs.code_hash, results.code AS matched_code
            FROM results
            JOIN gist_snippets gs ON results.hash = ANY(gs.code_hash)
        ),
        with_code AS (
            SELECT
                id, path, title, text, code_hash,
                array_agg(matched_code) AS code_array
            FROM joined
            GROUP BY id, path, title, text, code_hash
        )
        SELECT sr.*
        FROM with_code c
        CROSS JOIN LATERAL snippet_search_result_row(c.id, c.title, c.path, c.text, c.code_array) AS sr
        LIMIT 10;
    `;
    return (rows as unknown as LegacySearchRow[]).map(snippetFromLegacyRow);
}

/**
 * Trigram similarity search over codeblock content.
 * @param query - Search string for trigram similarity on code_flat
 * @returns Snippet rows with snippets as Block[]
 */
export async function snippetsFtsQuery(query: string, sql: Sql): Promise<Snippet[]> {
    const rows = await sql`
        WITH results AS (
            SELECT *
            FROM gist_codeblocks
            WHERE coalesce(code_flat, '') % ${query}
        ),
        joined AS (
            SELECT gs.id, gs.path, gs.title, gs.text, gs.code_hash, results.code AS matched_code
            FROM results
            JOIN gist_snippets gs ON results.hash = ANY(gs.code_hash)
        ),
        with_code AS (
            SELECT
                id, path, title, text, code_hash,
                array_agg(matched_code) AS code_array
            FROM joined
            GROUP BY id, path, title, text, code_hash
        )
        SELECT sr.*
        FROM with_code c
        CROSS JOIN LATERAL snippet_search_result_row(c.id, c.title, c.path, c.text, c.code_array) AS sr
        LIMIT 10;
    `;
    return (rows as unknown as LegacySearchRow[]).map(snippetFromLegacyRow);
}

export async function runQuery<T>(query: string, sql: Sql): Promise<T> {
    const res = await sql.unsafe(query) as T;
    return res;
}
