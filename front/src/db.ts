import Dexie, { type EntityTable } from 'dexie';
import type { QueryResponse } from './lib/api.contract';

type QueryCache = {
    query: string;
} & QueryResponse;

var db = new Dexie("db") as Dexie & {
    queries: EntityTable<QueryCache, 'query'>;
};

db.version(1).stores({
    queries: "&query"
});

// (() => {
//     console.log("adding to db");
//     db.queries.add({
//         query: "foo1",
//         snippet_ids: []
//     })
// })()
export type { QueryCache };
export { db };