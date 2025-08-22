import Dexie, {type EntityTable} from 'dexie';

interface Query{
    id: number, 
    query: string,
    response: object
}


var db = new Dexie("db") as Dexie & {
    queries: EntityTable<Query, 'id'>;
};

db.version(1).stores({
    queries: "++id, query, response"
})

export type {Query};
export {db};