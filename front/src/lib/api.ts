import { logger } from "$lib/logger";
import DOMPurify from 'dompurify';
import { db, type QueryCache } from '../db';
import { QueryEndpointResponseSchema, type QueryEndpointResponse } from './api.contract';
import { ENDPOINTS } from './const';
import type { Snippet } from './types';

const log = logger.child({ service: "api" });

var sanitise = DOMPurify.sanitize;
var base_url = (): URL => new URL(window.location.origin);


export async function query(query: string): Promise<QueryEndpointResponse> {
    log.info({ query: query }, "Sending query");

    const q: string = sanitise(query);
    const url: URL = new URL(ENDPOINTS.query, base_url());
    url.searchParams.append("q", query);

    logger.info({ url: url.toString() }, "Sending query");

    const res = await fetch(url, { method: "get" });
    if (!(res.status >= 200 && res.status < 300)) { }

    const response_json = await res.json();
    logger.info(response_json, "Response");

    const response = QueryEndpointResponseSchema.parse(response_json);
    return response;
}

export async function cacheResponseSnippets(queryCache: QueryCache): Promise<Snippet[]> {
    logger.info("Caching response");
    try {
        const row_id = await db.queries.put(queryCache);
        logger.info(["Cached. Row id: ", row_id, "Response: ", queryCache]);
    } catch (err) {
        logger.error(err, "error with putting response into queries table");
    }
    return queryCache.snippets;
}

export async function sync(): Promise<boolean> {
    logger.info("Clear table")
    let db_has_cleared = await clearTable();
    logger.info(["Clear table: ", db_has_cleared]);

    logger.info("Call sync endpoint");
    let url: URL = new URL(ENDPOINTS.sync, base_url());
    let res = await fetch(url, { method: "post" });
    if (!(res.status >= 200 && res.status < 300)) {
        throw new Error("Failed")
    }
    // let response = <Response> await res.json();
    // logger.info("Response: ", response || "Failed to parse response");
    // return response;
    return true;
}

async function clearTable(): Promise<boolean> {
    logger.info("Clearning database")
    await db.queries.clear();
    let table_count = await db.queries.count();
    let clear_success = table_count == 0;
    logger.info(["row count = ", table_count]);

    if (!clear_success) {
        // error handle if the databse failed to clear
    }

    return clear_success
}

export async function queryInDb(query: string): Promise<Snippet[] | undefined> {
    const row = await db.queries.get({ query });
    return row?.snippets;
}