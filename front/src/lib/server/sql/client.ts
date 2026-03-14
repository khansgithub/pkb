import { PRIVATE_PGHOST, PRIVATE_PGPORT, PRIVATE_PGSSLMODE, DEBUG } from "$env/static/private";
import postgres from "postgres";
import { codeblocksFtsQuery, codeblocksTrigramQuery, snippetsFtsQuery, snippetsTrigramQuery } from "./queries";
import type { Snippet } from "$lib/types";
import { logger } from "$lib/logger";

const log = logger.child({ module: "sql_client", level: "debug" });


const defaultConnectionOptions = {
    host: "127.0.0.1",
    port: 5432,
    ssl: false,
    debug: false,
    connect_timeout: 10,
    max: 1,
    onnotice: () => { },
} as const;

/** Connection options from .env (PGHOST, PGPORT, PGSSLMODE) with safe defaults. */
function getConnectionOptions(): Record<string, unknown> {
    const host = PRIVATE_PGHOST ?? defaultConnectionOptions.host;
    const port = Number(PRIVATE_PGPORT ?? defaultConnectionOptions.port);
    const ssl = PRIVATE_PGSSLMODE === "require";
    const debug = DEBUG === "1";
    return {
        ...defaultConnectionOptions,
        host: host,
        port: port,
        ssl: ssl,
        debug: debug,
    };
}

export type RunQueryResult =
    | { ok: true; snippets: Snippet[] }
    | { ok: false; error: Error };


/**
 * Runs search queries (FTS + trigram for snippets and codeblocks), merges by id, and returns
 * a result object. Connection errors and query errors are caught; partial results are returned
 * when only some queries fail.
 */
export async function runQuery(queryString: string): Promise<RunQueryResult> {
    let sql: postgres.Sql | null = null;
    log.debug({ queryString }, "runQuery called");

    try {
        log.debug("Attempting to create postgres client with connection options");
        sql = postgres(getConnectionOptions());
        // Check if the client can actually connect to the database
        await sql`SELECT 1`;
        log.debug("Postgres client created successfully");
    } catch (e) {
        const err = e instanceof Error ? e : new Error(String(e));
        log.error({ error: err }, "Connection failed while creating postgres client");
        return { ok: false, error: err };
    }

    try {
        log.debug("About to run query promises in parallel (trigram+fts/snippets+codeblocks)");
        const [trigramSnippets, ftsSnippets, ftsCodeblocks, trigramCodeblocks] = await Promise.allSettled([
            snippetsTrigramQuery(queryString, sql),
            snippetsFtsQuery(queryString, sql),
            codeblocksFtsQuery(queryString, sql),
            codeblocksTrigramQuery(queryString, sql),
        ]);
        log.debug({
            trigramSnippets,
            ftsSnippets,
            ftsCodeblocks,
            trigramCodeblocks
        }, "All query promises settled");

        const rows: Snippet[] = [];
        const reasons: unknown[] = [];

        for (const [label, result] of [
            ["snippetsTrigram", trigramSnippets],
            ["snippetsFts", ftsSnippets],
            ["codeblocksFts", ftsCodeblocks],
            ["codeblocksTrigram", trigramCodeblocks],
        ] as const) {
            log.debug({ label, result }, "Inspecting query result");
            if (result.status === "fulfilled") {
                log.debug({ label, value: result.value }, `Query "${label}" fulfilled, rows: ${result.value?.length ?? 0}`);
                rows.push(...result.value);
            } else {
                log.warn({
                    label,
                    error: result.reason
                }, `Query "${label}" rejected`);
                reasons.push({ query: label, error: result.reason });
            }
        }

        if (reasons.length > 0) {
            log.warn({ reasons: reasons }, "Some queries failed");
        } else {
            log.debug("All queries succeeded");
        }

        const snippets: Record<string, Snippet> = {};
        for (const row of rows) {
            const id = row.id;
            log.debug({ row, id }, "Processing row to collect snippets by id");
            if (id !== undefined && id !== null) {
                // If duplicate id, the latest result will overwrite the previous one.
                snippets[String(id)] = row;
            } else {
                log.warn({ row }, "Snippet row is missing id");
            }
        }
        log.debug({ snippetsCount: Object.keys(snippets).length }, "Final snippets compiled");

        return { ok: true, snippets: Object.values(snippets) };

    } catch (e) {
        const err = e instanceof Error ? e : new Error(String(e));
        log.error({ error: err }, "Caught exception during query logic in runQuery");
        return { ok: false, error: err };
    } finally {
        if (sql) {
            log.debug("Closing postgres client connection");
            try {
                await sql.end();
                log.debug("Postgres client connection closed successfully");
            } catch (endErr) {
                log.warn({ error: endErr }, "end() failed when closing postgres client");
            }
        } else {
            log.debug("No postgres client to close in finally block");
        }
    }
}
