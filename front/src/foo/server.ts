import { PGlite } from '@electric-sql/pglite'
import { PGLiteSocketServer } from '@electric-sql/pglite-socket'
import { createDb } from './db';
import { seed } from './seed';
import { getQuery } from './queries';
import type { TsVectorQueryRow, TrigramQueryRow, CodeblocksTsVectorRow, CodeblocksTrigramRow } from './sql/types';

const db = await createDb();
await seed(db);

async function ftsQuery<F extends readonly string[]>(
    db: PGlite,
    table: string,
    tsvectorColumn: string,
    queryFieldList: F,
    queryString: string
): Promise<TsVectorQueryRow<F>[]> {
    const sql = `
        SELECT ${queryFieldList.join(",")}
        FROM ${table}
        WHERE to_tsvector(${tsvectorColumn}) @@ plainto_tsquery($1)`;
    const res = await db.query(sql, [queryString]);
    return res.rows as TsVectorQueryRow<F>[];
}

async function trigramQuery<F extends readonly string[]>(
    db: PGlite,
    table: string,
    column: string,
    queryFieldList: F,
    queryString: string,
    similarityThreshold?: number
): Promise<TrigramQueryRow<F>[]> {
    if (similarityThreshold !== undefined) {
        await db.query(`SELECT set_limit($1);`, [similarityThreshold]);
    }
    const sql = `
        SELECT ${queryFieldList.join(",")}
        FROM ${table}
        WHERE ${column} % $1

        ORDER BY similarity(${column}, $1) DESC
    `;
    const res = await db.query(sql, [queryString]);
    return res.rows as TrigramQueryRow<F>[];
}

const queryString = "redis";
const queryFields = ["hash", "code"] as const;
const codeblocksFtsQuery: CodeblocksTsVectorRow[] = await ftsQuery(
    db,
    "gist_codeblocks",
    "code_flat",
    ["hash", "code"],
    queryString
);

const codeblocksTrgrmQuery: CodeblocksTrigramRow[] = await trigramQuery(
    db,
    "gist_codeblocks",
    "code_flat",
    ["hash", "code"],
    queryString
);

const snippetsFtsQuery = await ftsQuery(
    db,
    "gist_snippets",
    "text_flat",
    [],
    queryString
)
let q = "redis";
const r = await db.query(getQuery('snippets_fts'), [q]);
console.log(JSON.stringify(r.rows, null, 2));


// for (const row of rows.flat()) {
//     console.log(row.hash);
// }


await db.close();

// const server = new PGLiteSocketServer({
//     db,
//     port: 5432,
//     host: '127.0.0.1',
//     debug: true,
// })
// await server.start()
// console.log('Server started on 127.0.0.1:5432')
// let r = await server.db.exec("SELECT current_database();");
// console.log(JSON.stringify(r));

// process.on('SIGINT', async () => {
//     await server.stop()
//     await db.close()
//     console.log('Server stopped and database closed')
//     process.exit(0)
// });