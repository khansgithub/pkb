-- =============================================================================
-- queries.sql
-- =============================================================================
-- Search and lookup queries for gist snippets and codeblocks.
-- Uses helpers from create_db.sql: snippet_searchable_text, expand_code_hashes,
-- snippet_search_result_row.
-- =============================================================================
-- =============================================================================
-- query:snippets_fts
-- =============================================================================
-- Full-text search over snippet text and path (simple config).
-- @param $1: string - Full-text search query for plainto_tsquery
-- @returns id: number, title: string, tags: string[], description: string | null, snippets: string[]
WITH
  matched AS (
    SELECT
      *
    FROM
      gist_snippets
    WHERE
      to_tsvector(
        'simple',
        snippet_searchable_text (text_flat, path)
      ) @@ plainto_tsquery('simple', $1)
  ),
  with_code AS (
    SELECT
      *,
      expand_code_hashes (code_hash) AS code_array
    FROM
      matched
  )
SELECT
  sr.*
FROM
  with_code c
  CROSS JOIN LATERAL snippet_search_result_row (c.id, c.title, c.path, c.text, c.code_array) AS sr
LIMIT
  10;

-- end
-- =============================================================================
-- query:snippets_trigram
-- =============================================================================
-- Trigram similarity search over snippet text and path.
-- @param $1: string - Search string for trigram similarity matching
-- @returns id: number, title: string, tags: string[], description: string | null, snippets: string[]
WITH
  trigram_snippets AS (
    SELECT
      *,
      similarity (snippet_searchable_text (text_flat, path), $1) AS sim
    FROM
      gist_snippets
    WHERE
      snippet_searchable_text (text_flat, path) % $1
  ),
  with_code AS (
    SELECT
      ts.*,
      expand_code_hashes (ts.code_hash) AS code_array
    FROM
      trigram_snippets ts
  ),
  ordered AS (
    SELECT
      *,
      row_number() OVER (
        ORDER BY
          sim DESC
      ) AS rn
    FROM
      with_code
  )
SELECT
  sr.title,
  sr.tags,
  sr.description,
  sr.snippets
FROM
  ordered o
  CROSS JOIN LATERAL snippet_search_result_row (o.id, o.title, o.path, o.text, o.code_array) AS sr
ORDER BY
  o.rn
LIMIT
  10;

-- end
-- =============================================================================
-- query:codeblocks_fts
-- =============================================================================
-- Full-text search over codeblock content (english config).
-- @param $1: string - Full-text search query for plainto_tsquery
-- @returns id: number, title: string, tags: string[], description: string | null, snippets: string[]
WITH
  results AS (
    SELECT
      *
    FROM
      gist_codeblocks
    WHERE
      to_tsvector('english', coalesce(code_flat, '')) @@ plainto_tsquery('english', $1)
  ),
  joined AS (
    SELECT
      gs.id,
      gs.path,
      gs.title,
      gs.text,
      gs.code_hash,
      results.code AS matched_code
    FROM
      results
      JOIN gist_snippets gs ON results.hash = ANY (gs.code_hash)
  ),
  with_code AS (
    SELECT
      id,
      path,
      title,
      text,
      code_hash,
      array_agg(matched_code) AS code_array
    FROM
      joined
    GROUP BY
      id,
      path,
      title,
      text,
      code_hash
  )
SELECT
  sr.*
FROM
  with_code c
  CROSS JOIN LATERAL snippet_search_result_row (c.id, c.title, c.path, c.text, c.code_array) AS sr
LIMIT
  10;

-- end
-- =============================================================================
-- query:set_trigram_limit
-- =============================================================================
-- Set pg_trgm similarity threshold for % operator.
-- @param $1: number - Similarity threshold for pg_trgm % operator (0.0-1.0)
-- @returns set_limit: number
SELECT
  set_limit ($1);

-- end
-- =============================================================================
-- query:codeblocks_trigram
-- =============================================================================
-- Trigram similarity search over codeblock content.
-- @param $1: string - Search string for trigram similarity on code_flat
-- @returns id: number, title: string, tags: string[], description: string | null, snippets: string[]
WITH
  results AS (
    SELECT
      *
    FROM
      gist_codeblocks
    WHERE
      coalesce(code_flat, '') % $1
  ),
  joined AS (
    SELECT
      gs.id,
      gs.path,
      gs.title,
      gs.text,
      gs.code_hash,
      results.code AS matched_code
    FROM
      results
      JOIN gist_snippets gs ON results.hash = ANY (gs.code_hash)
  ),
  with_code AS (
    SELECT
      id,
      path,
      title,
      text,
      code_hash,
      array_agg(matched_code) AS code_array
    FROM
      joined
    GROUP BY
      id,
      path,
      title,
      text,
      code_hash
  )
SELECT
  sr.*
FROM
  with_code c
  CROSS JOIN LATERAL snippet_search_result_row (c.id, c.title, c.path, c.text, c.code_array) AS sr
LIMIT
  10;

-- end
