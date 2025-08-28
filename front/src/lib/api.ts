import DOMPurify from 'dompurify';
import { db, type Query } from '../db';
import { BACKEND, ENDPOINTS } from './const';
import { observeObject } from './debug';
import { logger as app_logger } from './logger';

const logger = app_logger.child({service: "api"});

var sanitise = DOMPurify.sanitize;
var base_url = (): URL => new URL(BACKEND)

// export interface Response extends Query { };

export class Response implements Query{
    query: string
    snippet_ids: Number[];
    constructor(query: string, snippets_id: Number[]){
        this.query = query;
        this.snippet_ids = snippets_id;
        Object.freeze(this); // getting a strange error where dexie.put would change `this.query`
    }
}

export async function send(query: string): Promise<Response> {
    let q: string = sanitise(query);
    logger.info("Sending POST with santisied query: " + q);
    let url: URL = new URL(ENDPOINTS.query, base_url());
    url.searchParams.append("q", query);

    let res = await fetch(url, { method: "post" });
    if (!(res.status >= 200 && res.status < 300)) {}
    let response_json = await res.json() as Query;
    let response = new Response(response_json.query, response_json.snippet_ids);
    logger.info(response || {}, "Response");
    return response;
}

export async function cacheResponse(response: Response): Promise<Response> {
    logger.info("Caching response");
    try {
        let row_id = await db.queries.put(response, response.query);
        logger.info(["Cached. Row id: ", row_id]);
    } catch (err) {
        console.error("error with putting response into queries table")
    }
    return response;
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

export async function queryInDb(query: string): Promise<Response | undefined> {
    return await db.queries.get(query);
}