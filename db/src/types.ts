export type BlockType = "code" | "text";

export type Snippet = {
    id?: number,
    title: string,
    tags: string[],
    description: string | null,
};

export type Block = {
    id?: number,
    type: BlockType,
    lang: string,
    lines: string[],
    snippet_id?: number,
    pos?: number
};

export type Row = Snippet & { blocks: Block[] };