/**
 * Seed the database with merged_gists.json data.
 * Run from project root: npx tsx front/src/foo/seed.ts
 * Or: node --loader ts-node/esm front/src/foo/seed.ts
 */
import type { PGlite } from '@electric-sql/pglite';
import { insertData } from './db';

// async function main() {
// 	const db = await createDb();
// 	const count = await insertData(db);
// 	console.log(`Inserted ${count} snippets into gist_snippets`);
// 	await db.close();
// }

export async function seed(db?: PGlite) {
	if (db === undefined) throw new Error("Database not passed");
	const count = await insertData(db);
	console.log(`Inserted ${count} snippets into gist_snippets`);
}

// main().catch((err) => {
// 	console.error(err);
// 	process.exit(1);
// });
