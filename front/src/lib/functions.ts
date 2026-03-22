
import { queryInDb, cacheResponseSnippets, query } from "./api";
import type { Snippet } from "./types";
import { logger } from "$lib/logger";
import { isErrorResponse } from "./api.contract";
import { browser } from "$app/environment";

const log = logger.child({ module: "search_box" });

export async function getSnippetsFromQuery(
    queryString: string,
    errorMessage: string | null,
): Promise<[Snippet[], string | null]> {
    const cached_query = await queryInDb(queryString);
    let snippets: Snippet[] = [];
    if (cached_query && cached_query.length > 0) {
        log.info({ cached_query }, "Cached result found");
        snippets = cached_query;
    } else {
        log.info({ queryString }, "No cached result found, sending POST");
        const response = await query(queryString);
        if (isErrorResponse(response)) {
            log.error(
                { error: response.error },
                "Error received from query",
            );
            errorMessage =
                response.error?.message ??
                response.error?.name ??
                "Something went wrong";
            return [[], errorMessage];
        }
        errorMessage = null;
        snippets = await cacheResponseSnippets({
            query: queryString,
            snippets: response.snippets,
        });
    }
    return [snippets, errorMessage];
}


export function isMobile() {
    if (!browser) {
        return {
            isMobile: false,
            isTouch: false,
            isMobileScreen: false
        };
    }

    const isMobileScreen = window.matchMedia("(max-width: 768px)").matches;
    const isTouch = navigator.maxTouchPoints > 0;

    return isMobileScreen && isTouch
}