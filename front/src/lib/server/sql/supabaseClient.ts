import { createClient } from "@supabase/supabase-js";
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY } from "$env/static/public";
import type { Database } from "./supabase.types";
import type { CompositeTypes } from "./supabase.types";

const supabaseUrl = PUBLIC_SUPABASE_URL;
const supabaseKey = PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY;
export const supabase = createClient<Database>(supabaseUrl, supabaseKey);

export type FullSearchRow = CompositeTypes<"query_result">;

export type QueryResult = {
	data: FullSearchRow[] | null;
	error: Error | null;
};

/**
 * Runs the full_search RPC (FTS + trigram over snippets and codeblocks).
 */
export async function query(searchQuery: string): Promise<QueryResult> {
	const { data, error } = await supabase.rpc("full_search", { q: searchQuery });
	return {
		data: data ?? null,
		error: error ? new Error(error.message) : null,
	};
}