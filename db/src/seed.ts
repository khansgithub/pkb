/**
 * Seed the database with merged_gists.json data.
 * Run from project root: npx tsx front/src/foo/seed.ts
 * Or: node --loader ts-node/esm front/src/foo/seed.ts
 */
import type { PGlite } from '@electric-sql/pglite';
// import { insertData } from './db';


// async function main() {
// 	const db = await createDb();
// 	const count = await insertData(db);
// 	console.log(`Inserted ${count} snippets into gist_snippets`);
// 	await db.close();
// }

export async function seed(db?: PGlite) {
	if (db === undefined) throw new Error("Database not passed");
	const count = await insertData2(db);
	console.log(`Inserted ${count} snippets into gist_snippets`);
}

import rowData from "./data/rows.json";
import type { Snippet, Block, Row, BlockType } from './types';
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------

function generateSnippetValues(title: string, tags: string[], description: string) {
	const tagsString = `{${tags.join(",")}}`;
	return `('${title}','{${tagsString}}','${description}')`;
}

function generateSnippetParameters(offset: number = 0) {
	const string = "($x, $y, $z)"
		.replace("x", `${offset + 1}`)
		.replace("y", `${offset + 2}`)
		.replace("z", `${offset + 3}`);
	return {
		string: string,
		offset: offset + 3
	};
	// const valuesStatement = Array.from({ length: row.blocks.length }).map(
	//     (_, i) => `$${i * row.blocks.length + 1}, $${i * row.blocks.length + 2}, $${i * row.blocks.length + 3}`
	// ).join(",");

}

function generateBlockParameters(offset: number = 0) {
	const string = "($x, $y, $z::text[], $a::smallint)"
		.replace("x", `${offset + 1}`)
		.replace("y", `${offset + 2}`)
		.replace("z", `${offset + 3}`)
		.replace("a", `${offset + 4}`);
	return {
		string: string,
		offset: offset + 4
	}
}

function generateInsertSql(snippetParams: string[], blockParams: string[]) {
	const insertSql = /* sql */`
		WITH new_snippets AS (
			INSERT INTO snippets (title, tags, description)
			VALUES
				---------------- snippet ----------------
				${snippetParams.join(",")}
			RETURNING id AS snippet_id
		),
		blocks_to_insert AS (
			SELECT *
			FROM (VALUES
				---------------- blocks ----------------
				${blockParams.join(",")}
			) AS b(type, lang, lines, pos)
		),
		numbered_snippets AS (
			SELECT snippet_id, ROW_NUMBER() OVER () AS rn
			FROM new_snippets
		),
		numbered_blocks AS (
			SELECT type, lang, lines, pos, ROW_NUMBER() OVER () AS rn
			FROM blocks_to_insert
		)
		INSERT INTO blocks(type, lang, lines, pos, snippet_id)
		SELECT
			nb.type::block_type,
			nb.lang,
			nb.lines,
			nb.pos,
			ns.snippet_id
		FROM numbered_snippets ns
		JOIN numbered_blocks nb USING (rn);
	`;
	return insertSql;
}

async function insertData2(db: PGlite) {
	let offset = 0;
	const snippetParams: string[] = [];
	const blockParams: string[] = [];
	const data: any[] = [];

	// const rows = [rowData[5]] as Row[];
	const rows = rowData.slice(0) as Row[];

	for (const row of rows) {
		const snippetParam = generateSnippetParameters(offset);
		snippetParams.push(snippetParam.string);
		offset = snippetParam.offset;

		data.push(row.title, row.tags, row.description);
		row.blocks.forEach((block, i) => {
			const blockParam = generateBlockParameters(offset);
			offset = blockParam.offset;
			blockParams.push(blockParam.string);
			data.push(block.type, block.lang ?? "plaintext", block.lines, i + 1)
		});
	}

	const insertSql = generateInsertSql(snippetParams, blockParams);
	// console.log(insertSql);
	// console.log(data);

	const result = await db.query(insertSql, data);
	console.log(result);
	return result.rows.length;
}

// await seed();

// main().catch((err) => {
// 	console.error(err);
// 	process.exit(1);
// });
