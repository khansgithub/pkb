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
      ) @@ plainto_tsquery('simple', 'redis')
  ),
  with_code AS (
    SELECT
      id,
      title,
      path,
      text,
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

-- WITH
--   A AS (
--     SELECT
--       code_hash,
--       expand_code_hashes (code_hash) AS code_array
--     FROM
--       gist_snippets
--     limit
--       1
--   ),
--   B as (
--     select
--       A.code_array,
--       generate_series(1, array_upper((A.code_array)::text[] [], 1))
--     from
--       A
--   )
-- SELECT
--   *
-- FROM
--   B;
-- select *
-- from (
--   select * from gist_snippets where cardinality(code_hash) = 2 fetch first 1 row only
-- ) as s
-- cross join gist_codeblocks
-- fetch first 3 row only;
