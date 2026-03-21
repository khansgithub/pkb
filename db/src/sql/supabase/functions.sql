drop function if exists snippets_fts_query (text);

drop function if exists snippets_trgm_query (text);

drop function if exists blocks_trgm_query (text);

drop function if exists blocks_fts_query (text);

drop function if exists full_search (text);

drop type IF exists query_result CASCADE;

create type query_result as (
  id integer,
  title text,
  tags text[],
  description text,
  type block_type,
  lang text,
  lines text[],
  pos smallint
);

-----------------------------------------------------------------------------------------------------------------------------
-- blocks_trgm_query --
-----------------------------------------------------------------------------------------------------------------------------
create or replace function blocks_trgm_query (q text) returns setof query_result language sql stable as $$
with
  matched_block as (
    select
      *,
      array_to_string_immut (lines) as flat,
      similarity (
        array_to_string_immut (lines),
        q
      ) as sim
    from
      blocks
    where
      array_to_string_immut (lines) % q
  )
select
  snippets.id,
  snippets.title,
  snippets.tags,
  snippets.description,
  matched_block.type,
  matched_block.lang,
  matched_block.lines,
  matched_block.pos
from
  matched_block
  left join snippets on matched_block.snippet_id = snippets.id
  order by sim desc
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- blocks_fts_query --
-----------------------------------------------------------------------------------------------------------------------------
create or replace function blocks_fts_query (q text) returns setof query_result language sql stable as $$
with
  matched_block as (
    select
      *
    from
      blocks
    where
      to_tsvector('simple', array_to_string_immut (lines)) @@ plainto_tsquery('simple', q)
  )
select
  snippets.id,
  snippets.title,
  snippets.tags,
  snippets.description,
  matched_block.type,
  matched_block.lang,
  matched_block.lines,
  matched_block.pos
from
  matched_block
  left join snippets on matched_block.snippet_id = snippets.id
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- snippets_trgm_query --
-----------------------------------------------------------------------------------------------------------------------------
create or replace function snippets_trgm_query (q text) returns setof query_result language sql stable as $$
with
  matched_metadata as (
    select
      *,
      array_to_string_immut (array[title, description] || tags) as flat,
      similarity (
        array_to_string_immut (array[title, description] || tags),
        q
      ) as sim
    from
      snippets
    where
      array_to_string_immut (array[title, description] || tags) % q
  )
select
  matched_metadata.id,
  matched_metadata.title,
  matched_metadata.tags,
  matched_metadata.description,
  blocks.type,
  blocks.lang,
  blocks.lines,
  blocks.pos
from matched_metadata
left join blocks on matched_metadata.id = blocks.snippet_id
order by sim desc
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- snippets_fts_query ---
-----------------------------------------------------------------------------------------------------------------------------
create or replace function snippets_fts_query (q text) returns setof query_result language sql stable as $$
with matched_metadata as (
  select *
  from snippets
  where
    to_tsvector(
      'simple',
      array_to_string_immut(array[title, description] || tags)
    ) @@ plainto_tsquery('simple', q)
)
select
  matched_metadata.id,
  matched_metadata.title,
  matched_metadata.tags,
  matched_metadata.description,
  blocks.type,
  blocks.lang,
  blocks.lines,
  blocks.pos
from matched_metadata
left join blocks on matched_metadata.id = blocks.snippet_id;
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- full_search
-----------------------------------------------------------------------------------------------------------------------------
create or replace function full_search (q text) returns setof query_result language sql stable as $$
WITH
_1 AS (SELECT * FROM snippets_trgm_query(q)),
_2 AS (SELECT * FROM snippets_fts_query(q)),
_3 AS (SELECT * FROM blocks_fts_query(q)),
_4 AS (SELECT * FROM blocks_trgm_query(q)),
combined AS (
    SELECT * FROM _1
    UNION ALL
    SELECT * FROM _2
    UNION ALL
    SELECT * FROM _3
    UNION ALL
    SELECT * FROM _4
)
SELECT DISTINCT ON (id) *
FROM combined
ORDER BY id DESC;
$$;