import { PGLiteSocketServer } from '@electric-sql/pglite-socket';
import { createDb } from './db';
import { snippetsTrigramQuery, snippetsFtsQuery, codeblocksFtsQuery, codeblocksTrigramQuery } from './query';
import { seed } from './seed';

const db = await createDb();
await seed(db);

// {
//     const queryString = "redis";

//     const rows = [
//         await snippetsTrigramQuery(db, [queryString]),
//         await snippetsFtsQuery(db, [queryString]),
//         await codeblocksFtsQuery(db, [queryString]),
//         await codeblocksTrigramQuery(db, [queryString]),
//     ];

//     const snippets = Object.fromEntries(rows.flatMap(r => r.map(curr => [curr.id, curr])));
//     console.log(JSON.stringify(snippets, null, 2));

//     await db.close
// }

// ------------------------------------------------------------

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