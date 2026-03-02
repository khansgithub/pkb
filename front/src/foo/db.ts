import { PGlite } from '@electric-sql/pglite'
import { pg_trgm } from '@electric-sql/pglite/contrib/pg_trgm';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const create_db_sql = loadSql("create_db.sql");

type BlockEnum = "code" | "text";

interface CodeBlock {
    lang: string;
    code: string[]; // JSON serialization alias for lines
    block_type?: BlockEnum;
}

interface TextBlock {
    text: string[]; // JSON serialization alias for lines
    block_type?: BlockEnum;
}

type SnippetBlock = CodeBlock | TextBlock;
type Snippets = SnippetBlock[];

interface Section {
    name: string;
    level: number;
    snippets: SnippetBlock[];
    children: Section[];
}

interface Section1 extends Section {
    hashes: Set<string> | string[]; // JSON serializes set as array
}

type SomeSection = Section1 | Section;

export type SnippetRow = {
    id?: number;
    path: string;
    title: string;
    // code: string[][] | null;
    codeHashes: string[];
    text: string[] | null;
    created_at?: string; // iso/timestamp
};

export type CodeblocksRows = {
    hash: string;
    code: string[];
};

function loadSql(filename: string) {
    return fs.readFileSync(path.join(__dirname, "sql", filename), "utf8");
}


function buildPath(sectionName: string, path?: string) {
    return `${path ? path + "/" : "/"}${sectionName}`;
}

function isCodeBlock(block: SnippetBlock): block is CodeBlock {
    return "lang" in block;
}

function getBlockLines(block: SnippetBlock): string[] {
    return isCodeBlock(block) ? block.code : block.text
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
): [SnippetRow, CodeblocksRows[]] {
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

    ] as [SnippetRow, CodeblocksRows[]];
    return out;
}

function findSnippet(section: SomeSection, path?: string, sectionHashGen?: Generator<string>): [SnippetRow[], CodeblocksRows[]] {
    const snippets = section.snippets;
    const hasSnippets = snippets.length > 0;

    const snippetRows: SnippetRow[] = [];
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

function buildRows(gists: Section1[]): [SnippetRow[], CodeblocksRows[]] {
    const snippetRows: SnippetRow[] = [];
    const codeblocksRows: CodeblocksRows[] = [];
    for (const section of gists) {
        function* sectionHashGen() { for (const h of section.hashes) yield h; }
        const [snippetRows_, codeblockRows_] = findSnippet(section, undefined, sectionHashGen());
        snippetRows.push(...snippetRows_);
        codeblocksRows.push(...codeblockRows_)
    }

    return [snippetRows, codeblocksRows];
}

export async function insertData(db: PGlite) {
    const jsonPath = path.join(__dirname, "data", "merged_gists.json");
    const json = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
    const [snippetRows, codeblocksRows] = buildRows(json);

    for (const codeblock of codeblocksRows) {
        try {
            await db.query(
                "insert into gist_codeblocks (hash, code, code_flat) values ($1, $2, $3);",
                // [s.path, s.title, s.code ?? [[]], s.text ?? [], flat_code, flat_text]
                [codeblock.hash, codeblock.code, codeblock.code.join("\n")]
            );
        } catch (err) {
            console.error(
                `Failed to insert row for path [${codeblock.hash}]`,
                "\nRow data:", [codeblock.code],
                "\nError:", err
            );
            process.exit(1);
        }
    }

    for (const snippet of snippetRows) {
        const flat_text = (snippet.text ?? []).join("\n");
        try {
            const rowId = ((await db.query(
                "insert into gist_snippets (path,title,text,text_flat,code_hash) values ($1, $2, $3, $4, $5)returning id;",
                // [s.path, s.title, s.code ?? [[]], s.text ?? [], flat_code, flat_text]
                [
                    snippet.path,
                    snippet.title,
                    // null,
                    snippet.text ?? [],
                    // null,
                    flat_text,
                    snippet.codeHashes,
                ]
            )).rows[0] as SnippetRow).id;

            for (const hash of snippet.codeHashes){
                await db.query(
                    "insert into snippet_codeblocks_hash_map (snippet_id, codeblock_hash) values ($1, $2);",
                    [rowId, hash]
                );
            }            
            
        } catch (err) {
            console.error(
                `Failed to insert row for path [${snippet.path}]`,
                "\nRow data:", {
                    path: snippet.path,
                    title: snippet.title,
                    text: snippet.text,
                    codeHashes: snippet.codeHashes
                },
                "\nError:", err
            );
            process.exit(1);
        }
    }

    return snippetRows.length + codeblocksRows.length;
}

export async function createDb() {
    const db = await PGlite.create({
        // dataDir: "pgdata",
        extensions: { pg_trgm },

    });
    await db.exec(create_db_sql);
    return db;
}