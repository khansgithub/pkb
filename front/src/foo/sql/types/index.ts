/**
 * Types for tsvector and trigram SQL queries in server.ts
 */

// --- Schema types (from create_db.sql) ---

export type GistCodeblocksRow = {
  hash: string;
  code: string[];
  code_flat: string;
};

export type GistSnippetsRow = {
  id: number;
  path: string;
  title: string;
  text: string[] | null;
  text_flat: string | null;
  created_at: string | null;
  code_hash: string[] | null;
};

// --- TsVector query ---

export type TsVectorQueryParams = {
  table: string;
  tsvectorColumn: string;
  queryFieldList: readonly string[];
  queryString: string;
};

/** Row type inferred from the selected field list */
export type TsVectorQueryRow<F extends readonly string[]> = {
  [K in F[number]]: K extends keyof GistCodeblocksRow
    ? GistCodeblocksRow[K]
    : K extends keyof GistSnippetsRow
      ? GistSnippetsRow[K]
      : unknown;
};

// --- Trigram query ---

export type TrigramQueryParams = {
  table: string;
  column: string;
  queryFieldList: readonly string[];
  queryString: string;
  similarityThreshold?: number;
};

/** Row type inferred from the selected field list */
export type TrigramQueryRow<F extends readonly string[]> = {
  [K in F[number]]: K extends keyof GistCodeblocksRow
    ? GistCodeblocksRow[K]
    : K extends keyof GistSnippetsRow
      ? GistSnippetsRow[K]
      : unknown;
};

// --- Concrete row types for known queries ---

/** Return type for tsvector query on gist_codeblocks selecting hash, code */
export type CodeblocksTsVectorRow = TsVectorQueryRow<readonly ["hash", "code"]>;

/** Return type for trigram query on gist_codeblocks selecting hash, code */
export type CodeblocksTrigramRow = TrigramQueryRow<readonly ["hash", "code"]>;
