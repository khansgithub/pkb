// This is what the database query output should look like, one row.
const x = {
    card: {
        id: "",
        title: "",
        tags: "",
        description: "",
        blocks: [
            {
                blockType: "code",
                lang: "python",
                lines: ["line1", "line2", , "line3"]
            },
            {
                blockType: "text",
                lines: ["line1", "line2", "line3"]
            }
        ]
    }
}

// In order to find this row, there needs to be a match on 1) code blocks 2) text blocks 3) title + tags + description
// This means these fields need to exist as flat strings in the database.

const rowToMatchAgainst = {
    id: FK_to_SnippetsDB,
    textMatch: "title + tags + description + all text blocks",
    codeMatch: "all code blocks",
}

const SnippetsDB = {
    id: PK,
    title: "",
    tags: "",
    description: "",
    // blocks: [
    //     FK_to_block_1,
    //     FK_to_block_2,
    // ]
}

const BlocksDB = {
    blockId: 1,
    type: "code" | "text",
    lang: undefined | "",
    lines: ["", "", ""],
    pos: number,
    snippetId: number

}

const insertSql = /* sql */`
WITH new_snippets AS (
    INSERT INTO snippets (title, tags, description)
    VALUES
        ('redis', '{redis}', ''),
        ('list keys', '{redis}', ''),
        ('read stream', '{redis}', ''),
        ('find keys and pipe to delete', '{redis}', '')
    RETURNING id AS snippet_id
),
blocks_to_insert AS (
    SELECT *
    FROM (VALUES
        ('code', 'bas', ARRAY['redis-cli'], 1),
        ('code', 'ba', ARRAY['keys *'], 1),
        ('code', 'b', ARRAY['xrange <key> - +'], 1),
        ('code', 'bashh', ARRAY['#             < query >', 'redis-cli keys rq:res* | awk ''{print $1}'' | xargs redis-cli del'], 1)
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
`