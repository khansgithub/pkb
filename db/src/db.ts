import { PGlite, type Results } from '@electric-sql/pglite'
import { pg_trgm } from '@electric-sql/pglite/contrib/pg_trgm';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import rowData from "./data/rows.json";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const create_db_sql = loadSql("create_db.sql");


interface CodeBlock {
    lang: string;
    lines: string[];
    type: BlockEnum;
}

interface TextBlock {
    lines: string[];
    type: BlockEnum;
}


type BlockEnum = "code" | "text";
type Block = CodeBlock | TextBlock;
type SomeSection = Section1 | Section;

export type Row = {
    id?: number;
    title: string;
    tags: string[];
    description: string;
    blocks: Block[];
    created_at?: string; // iso/timestamp
};


function loadSql(filename: string) {
    return fs.readFileSync(path.join(__dirname, "sql", filename), "utf8");
}

function buildPath(sectionName: string, path?: string) {
    return `${path ? path + "/" : "/"}${sectionName}`;
}

function isCodeBlock(block: Block): block is CodeBlock {
    return "lang" in block;
}

function getBlockLines(block: Block): string[] {
    return isCodeBlock(block) ? block.lines : block.lines
}

function isSection(node: unknown): node is Section {
    return (
        typeof node === "object" &&
        node !== null &&
        "name" in node &&
        "snippets" in node &&
        Array.isArray((node as Section).snippets)
    );
}

function rowFromSection(
    section: Section,
    path?: string,
    sectionHashGen?: Generator<string, string, string>
): [Row, CodeblocksRows[]] {
    const code: string[][] = [];
    const codeHashes: string[] = [];
    const other: string[] = [];
    const snippets = section.snippets ?? [];

    // for each snippet there is a hash entry for the snippet name, the codeblocks and textblocks
    if (section.name) sectionHashGen?.next();

    for (const block of snippets) {
        const lines = getBlockLines(block);
        const hash = sectionHashGen?.next().value ?? "";
        if (isCodeBlock(block)) {
            code.push(lines);
            codeHashes.push(hash);
        } else {
            other.push(...lines);
        }
    }

    const out = [
        {
            title: section.name,
            path: path ?? "/" + section.name,
            text: other.length > 0 ? other : null,
            // code: code.length > 0 ? code : null,
            codeHashes: codeHashes,
        },

        // ...code.map((block, i) => [codeHashes[i], block]),
        codeHashes.map((value, index) => {
            return {
                hash: value,
                code: code[index]
            }
        }) as CodeblocksRows[],

    ] as [Row, CodeblocksRows[]];
    return out;
}

function findSnippet(section: SomeSection, path?: string, sectionHashGen?: Generator<string>): [Row[], CodeblocksRows[]] {
    const snippets = section.snippets;
    const hasSnippets = snippets.length > 0;

    const snippetRows: Row[] = [];
    const codeblocksRows: CodeblocksRows[] = [];

    if (hasSnippets) {
        const [snippetRows_, codeblockRows_] = rowFromSection(section, path, sectionHashGen);
        snippetRows.push(snippetRows_);
        codeblocksRows.push(...codeblockRows_)
    }

    const children = section.children;
    for (const child of children) {
        if (isSection(child)) {
            const [snippetRows_, codeblockRows_] = findSnippet(
                child,
                buildPath(section.name, path),
                sectionHashGen);
            snippetRows.push(...snippetRows_);
            codeblocksRows.push(...codeblockRows_)

        }
    }

    return [snippetRows, codeblocksRows];
}



async function insertIntoBlocks(db: PGlite, row: Row): Promise<number[]> {
    const valuesStatement = Array.from({ length: row.blocks.length }).map(
        (_, i) => `$${i * row.blocks.length + 1}, $${i * row.blocks.length + 2}, $${i * row.blocks.length + 3}`
    ).join(",");


    for (const block of row.blocks) {
        try {
            const sql = /* sql*/ `insert into blocks (type, lang, lines) ${valuesStatement};`;
            const result: Results<Row> = await db.query(sql,
                [block.type, (block as CodeBlock).lang ?? null, block.lines]
            );
            return Array.from(result.rows).map(row => row.id!);
        } catch (err) {
            console.error(`Failed to insert block: [${block}]`);
            process.exit(1);
        }
    }
}

// export async function insertData(db: PGlite) {
//     // popular Blocks table
//     for (const row of rowData as Row[]) {
//         // all the block ids for this snippet
//         const blockIds = await insertIntoBlocks(db, row);


//         const flat_text = (snippet.text ?? []).join("\n");
//         try {
//             const rowId = ((await db.query(
//                 "insert into gist_snippets (path,title,text,text_flat,code_hash) values ($1, $2, $3, $4, $5)returning id;",
//                 // [s.path, s.title, s.code ?? [[]], s.text ?? [], flat_code, flat_text]
//                 [
//                     snippet.path,
//                     snippet.title,
//                     // null,
//                     snippet.text ?? [],
//                     // null,
//                     flat_text,
//                     snippet.codeHashes,
//                 ]
//             )).rows[0] as Row).id;

//             for (const hash of snippet.codeHashes) {
//                 await db.query(
//                     "insert into snippet_codeblocks_hash_map (snippet_id, codeblock_hash) values ($1, $2);",
//                     [rowId, hash]
//                 );
//             }

//         } catch (err) {
//             console.error(
//                 `Failed to insert row for path [${snippet.path}]`,
//                 "\nRow data:", {
//                 path: snippet.path,
//                 title: snippet.title,
//                 text: snippet.text,
//                 codeHashes: snippet.codeHashes
//             },
//                 "\nError:", err
//             );
//             process.exit(1);
//         }
//     }

//     return snippetRows.length + codeblocksRows.length;
// }

export async function createDb() {
    const db = await PGlite.create({
        // dataDir: "pgdata",
        extensions: { pg_trgm },

    });
    await db.exec(create_db_sql);
    return db;
}