import Dexie, { type EntityTable } from 'dexie';

interface Query {
    query: string, // PK
    snippet_ids: Array<Number>
}

var db = new Dexie("db") as Dexie & {
    queries: EntityTable<Query, 'query'>;
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
export type { Query };
export { db };