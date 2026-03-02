-- query:snippets_fts
-- Query 1: Get the concat field as "concat_field" (text_flat + ' ' + path)
WITH concat_snippets AS (
  SELECT 
    coalesce(text_flat, '') || ' ' || coalesce(REPLACE(path, '/', ' '), '') AS concat_field,
    text_flat,
    code_hash,
    REPLACE(path, '/', ' ') AS path
  FROM gist_snippets
  -- WHERE length(coalesce(text_flat, '')) > 0
),

-- Query 2: Apply to_tsvector to the concat_field, alias as "tsvector_field"
tsvector_snippets AS (
  SELECT 
    -- to_tsvector('simple', concat_field) AS tsvector_field,
    concat_field,
    text_flat,
    path,
    code_hash
  FROM concat_snippets
),

-- Query 3: Given code_hash, select code from gist_codeblocks
codeblocks_from_hashes AS (
  SELECT 
    tsvector_snippets.concat_field,
    tsvector_snippets.text_flat,
    tsvector_snippets.path,
    tsvector_snippets.code_hash,
    ARRAY(
      SELECT gc.code
      FROM UNNEST(tsvector_snippets.code_hash) AS code_hash_item
      JOIN gist_codeblocks gc ON gc.hash = code_hash_item
    ) AS code_array
  FROM tsvector_snippets
)

-- Final select, joining both FTS and code lookups.
SELECT * 
FROM codeblocks_from_hashes
WHERE to_tsvector('simple', concat_field) @@ plainto_tsquery($1)
LIMIT 10;
-- end
--
--
--
-- query:snippets_trigram
-- Trigram Query: Find similar text_flat + path fields using pg_trgm
WITH concat_snippets AS (
  SELECT 
    coalesce(text_flat, '') || ' ' || coalesce(path, '') AS concat_field,
    text_flat,
    path
  FROM gist_snippets
)
SELECT
  concat_field,
  text_flat,
  path,
  similarity(concat_field, $1) AS sim
FROM concat_snippets
WHERE concat_field % $1
ORDER BY sim DESC
LIMIT 10;
-- end