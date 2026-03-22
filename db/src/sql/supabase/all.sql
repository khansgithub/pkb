drop table if exists blocks CASCADE;

drop table if exists snippets CASCADE;

drop table if exists temp_snippets CASCADE;

drop table if exists temp_blocks CASCADE;

drop sequence IF exists snippets_id_seq cascade;

drop function if exists snippets_fts_query (text);

drop function if exists snippets_trgm_query (text);

drop function if exists blocks_trgm_query (text);

drop function if exists blocks_fts_query (text);

drop function if exists full_search (text);

drop type IF exists query_result CASCADE;

drop type IF exists block_type CASCADE;

-- types
create type block_type as ENUM('code', 'text');
CREATE SEQUENCE snippets_id_seq;

--tables
create table snippets (
  -- id integer generated always as identity not null unique primary key,
  id integer DEFAULT nextval('snippets_id_seq') not null primary key,
  title text not null default ''::text,
  tags text[] not null,
  description text not null default ''::text
);

create table blocks (
  id integer generated always as identity not null primary key,
  type block_type not null,
  lang text,
  lines text[] not null,
  snippet_id integer not null,
  pos smallint not null,
  constraint blocks_snippet_id_fkey foreign KEY (snippet_id) references public.snippets (id)
);

--indices - blocks
create index lines_flat_ts on blocks using GIN (
  to_tsvector('simple', array_to_string_immut (lines))
);

create index lines_flat_trgm on blocks using GIN (array_to_string_immut (lines) gin_trgm_ops);

--indices - snippets
create index snippet_flat_ts on snippets using GIN (
  to_tsvector(
    'simple',
    array_to_string_immut (array[title, description] || tags)
  )
);

create index snippet_flat_trgm on snippets using GIN (
  array_to_string_immut (array[title, description] || tags) gin_trgm_ops
);

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
-- FUNCTIONS ------------------------------------------------------------------------------------------------------------

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
-- blocks_trgm_query (IMPROVED)
-----------------------------------------------------------------------------------------------------------------------------
create or replace function blocks_trgm_query (q text) returns setof query_result language sql stable as $$
with
base as (
  select
    *,
    array_to_string_immut(lines) as flat
  from blocks
),
matched_block as (
  select
    *,
    similarity(flat, q) as sim,
    flat <-> q as dist
  from base
  where
    flat % q
    or flat ilike '%' || q || '%'
)
select
  s.id,
  s.title,
  s.tags,
  s.description,
  mb.type,
  mb.lang,
  mb.lines,
  mb.pos
from matched_block mb
left join snippets s on mb.snippet_id = s.id
order by
  sim desc nulls last,
  dist asc
limit 20;
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- blocks_fts_query (UNCHANGED)
-----------------------------------------------------------------------------------------------------------------------------
create or replace function blocks_fts_query (q text) returns setof query_result language sql stable as $$
with matched_block as (
  select *
  from blocks
  where
    to_tsvector('simple', array_to_string_immut(lines))
    @@ plainto_tsquery('simple', q)
)
select
  s.id,
  s.title,
  s.tags,
  s.description,
  mb.type,
  mb.lang,
  mb.lines,
  mb.pos
from matched_block mb
left join snippets s on mb.snippet_id = s.id;
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- snippets_trgm_query (IMPROVED + WEIGHTED)
-----------------------------------------------------------------------------------------------------------------------------
create or replace function snippets_trgm_query (q text) returns setof query_result language sql stable as $$
with base as (
  select
    *,
    array_to_string_immut(tags) as tags_flat
  from snippets
),
matched_metadata as (
  select
    *,
    -- weighted similarity
    similarity(title, q) * 2 +
    similarity(description, q) +
    similarity(tags_flat, q) * 1.5 as sim,
    -- best distance across fields
    least(
      title <-> q,
      description <-> q,
      tags_flat <-> q
    ) as dist
  from base
  where
    title % q
    or description % q
    or tags_flat % q
    or title ilike '%' || q || '%'
    or description ilike '%' || q || '%'
    or tags_flat ilike '%' || q || '%'
)
select
  mm.id,
  mm.title,
  mm.tags,
  mm.description,
  b.type,
  b.lang,
  b.lines,
  b.pos
from matched_metadata mm
left join blocks b on mm.id = b.snippet_id
order by
  sim desc nulls last,
  dist asc
limit 20;
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- snippets_fts_query (UNCHANGED)
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
  mm.id,
  mm.title,
  mm.tags,
  mm.description,
  b.type,
  b.lang,
  b.lines,
  b.pos
from matched_metadata mm
left join blocks b on mm.id = b.snippet_id;
$$;

-----------------------------------------------------------------------------------------------------------------------------
-- full_search (SLIGHTLY IMPROVED RANKING)
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

-- TEMP TABLES ------------------------------------------------------------------------

create table temp_snippets (
  id integer DEFAULT nextval('snippets_id_seq') not null primary key,
  title text not null default ''::text,
  tags text[] not null,
  description text not null default ''::text
);

create table temp_blocks (
  id integer generated always as identity not null primary key,
  type block_type not null,
  lang text,
  lines text[] not null,
  pos smallint not null,
  snippet_idx smallint not null default 1
);

-- INSERT --------------------------------------------------------------------------

-- 1) first populate 'snippets'
insert into snippets(id, title, tags, description)
select * from temp_snippets;

-- 2) then populate 'blcoks'
WITH a AS (
    SELECT 
        id AS snippet_id, 
        ROW_NUMBER() OVER () AS snippet_idx
    FROM temp_snippets
    -- LIMIT 20
)
insert into blocks(type, lang,lines, snippet_id, pos)
SELECT type,lang,lines,a.snippet_id,pos
FROM temp_blocks tb
JOIN a 
    ON tb.snippet_idx = a.snippet_idx;


-- QUERY ----------------------------------------------------------------------------
-- select * from full_search('python');