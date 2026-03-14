/** Auto-generated from create_db.sql and queries.sql - do not edit manually. Run: npm run generate:sql-types */

// --- Schema types (from create_db.sql) ---

export type GistSnippetsRow = {
  id: number;
  path: string;
  title: string;
  text: string[] | null;
  text_flat: string | null;
  created_at: string | null;
  code_hash: string[] | null;
};
export type GistCodeblocksRow = {
  hash: string;
  code: string[] | null;
  code_flat: string | null;
};
export type SnippetCodeblocksHashMapRow = {
  snippet_id: number | null;
  codeblock_hash: string | null;
};

// --- Query param and row types (from queries.sql) ---

export type QueryParamMap = {
  snippets_fts: [string];
  snippets_trigram: [string];
  codeblocks_fts: [string];
  set_trigram_limit: [number];
  codeblocks_trigram: [string];
};

export type QueryName = keyof QueryParamMap;

export type QueryRowMap = {
  snippets_fts: {
    id: number;
    title: string;
    tags: string[];
    description: string | null;
    snippets: string[];
  };
  snippets_trigram: {
    id: number;
    title: string;
    tags: string[];
    description: string | null;
    snippets: string[];
  };
  codeblocks_fts: {
    id: number;
    title: string;
    tags: string[];
    description: string | null;
    snippets: string[];
  };
  set_trigram_limit: {
    set_limit: number;
  };
  codeblocks_trigram: {
    id: number;
    title: string;
    tags: string[];
    description: string | null;
    snippets: string[];
  };
};

/** Row type for a specific query. Use with db.query(sql, params) result. */
export type QueryRow<K extends QueryName> = QueryRowMap[K];

// --- Row type aliases (one per query) ---

/** Row type for snippets_fts query */
export type SnippetsFtsRow = QueryRowMap['snippets_fts'];

/** Row type for snippets_trigram query */
export type SnippetsTrigramRow = QueryRowMap['snippets_trigram'];

/** Row type for codeblocks_fts query */
export type CodeblocksFtsRow = QueryRowMap['codeblocks_fts'];

/** Row type for set_trigram_limit query */
export type SetTrigramLimitRow = QueryRowMap['set_trigram_limit'];

/** Row type for codeblocks_trigram query */
export type CodeblocksTrigramRow = QueryRowMap['codeblocks_trigram'];
