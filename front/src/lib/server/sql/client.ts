import type { ErrorResponse, QueryEndpointResponse } from "$lib/api.contract";
import { query } from "./supabaseClient";
import type { FullSearchRow } from "./supabaseClient";
import type { Block, Snippet } from "$lib/types";
import { logger } from "$lib/logger";

const log = logger.child({ module: "sql_client", level: "debug" });

function queryErrorResponse(err: Error): ErrorResponse {
	return {
		error: {
			message: err.message,
			name: err.name,
			...(err.stack ? { stack: err.stack } : {}),
		},
	};
}

function rpcErrorResponse(error: { message: string } & Partial<Pick<Error, "name" | "stack">>): ErrorResponse {
	return {
		error: {
			message: error.message,
			name: typeof error.name === "string" ? error.name : "PostgrestError",
			...(error.stack ? { stack: error.stack } : {}),
		},
	};
}

function rowToBlock(row: FullSearchRow, snippetId: number): Block {
	log.debug({row} , "row");
	const type = row.type === "code" || row.type === "text" ? row.type : "text";
	return {
		type,
		lang: row.lang,
		lines: row.lines ?? [],
		snippet_id: snippetId,
		pos: row.pos ?? 0,
	};
}

/**
 * Maps full_search RPC rows (one per block) into Snippet[] by grouping by id
 * and collecting blocks into snippets arrays.
 */
function mapSearchRowsToSnippets(rows: FullSearchRow[]): Snippet[] {
	const byId = new Map<number, Snippet>();
	for (const row of rows) {
		const id = row.id;
		if (id === null || id === undefined) {
			log.warn({ row }, "Search row is missing id");
			continue;
		}
		const block = rowToBlock(row, id);
		const existing = byId.get(id);
		if (existing) {
			existing.snippets.push(block);
		} else {
			byId.set(id, {
				id,
				title: row.title ?? "",
				tags: row.tags ?? [],
				description: row.description ?? undefined,
				snippets: [block],
			});
		}
	}
	for (const s of byId.values()) {
		s.snippets.sort((a, b) => a.pos - b.pos);
	}
	return Array.from(byId.values());
}

/**
 * Runs full search via Supabase RPC (FTS + trigram for snippets and codeblocks),
 * maps results by snippet id, and returns API-shaped success or error payload.
 */
export async function runQuery(queryString: string): Promise<QueryEndpointResponse> {
	log.debug({ queryString }, "runQuery called");
	try {
		const { data, error } = await query(queryString);
		if (error) {
			log.error({ error }, "full_search RPC failed");
			return rpcErrorResponse(error);
		}
		const rows = data ?? [];
		log.debug({ rowCount: rows.length }, "full_search RPC succeeded");
		const snippets = mapSearchRowsToSnippets(rows);
		log.debug({ snippetsCount: snippets.length }, "Final snippets compiled");
		return { snippets };
	} catch (e) {
		const err = e instanceof Error ? e : new Error(String(e));
		log.error({ error: err }, "Caught exception in runQuery");
		throw e;
		return queryErrorResponse(err);
	}
}
