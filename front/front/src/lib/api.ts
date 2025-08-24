import DOMPurify from 'dompurify';
import {db, type Query } from '../db';

var sanitise = DOMPurify.sanitize;
var send_url = (): URL => new URL("");

export async function send(query: string): Promise<Query> {
    let q: string = sanitise(query);
    let cached_query = await queryInDb(q);
    if (cached_query) {
        console.log("cache found")
        return cached_query;
    }

    console.log("POST: ", q);

    // POST 
    let url: URL = send_url();
    url.searchParams.append("q", query);
    let res = await fetch(url, {method: "post"});
    if ( ! (res.status >= 200 && res.status < 300)) {
        // error handle response
    }

    return {
        "query": query,
        "snippet_ids": [
            0
        ]
    };
}

export async function sync() {
    let db_has_cleared = await clearTable();
    
}

async function clearTable(): Promise<boolean>{
    await db.queries.clear();

    console.log("Clearning database")
    let table_count = await db.queries.count();
    let clear_success = table_count == 0;
    console.log("row count = ", table_count);

    if (!clear_success){
        // error handle if the databse failed to clear
    }

    return clear_success
}

async function queryInDb(query:string): Promise<Query | undefined>{
    return await db.queries.get(query);
}