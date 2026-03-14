create extension if not exists pg_trgm;

------------------------------ snippets ------------------------------
-- table
create table gist_snippets (
  id serial primary key,
  path text not null,
  title text not null unique,
  -- code       text[][] null,
  -- code_flat  text null,
  text text[],
  text_flat text,
  created_at timestamptz default now(),
  code_hash text[]
  -- constraint at_least_one_content check (
  -- code is not null or text is not null
  -- )
);

-- create index idx_gist_snippets_text_flat_path
-- on gist_snippets
-- using gin (
--   to_tsvector('english', coalesce(text_flat, '') || ' ' || coalesce(path, ''))
-- );
CREATE INDEX idx_gist_snippets_fts ON gist_snippets USING gin (
  to_tsvector(
    'simple',
    coalesce(text_flat, '') || ' ' || coalesce(replace(path, '/', ' '), '')
  )
);

create index idx_gist_snippets_text_flat_path_trgm on gist_snippets using gin (
  (
    coalesce(text_flat, '') || ' ' || coalesce(replace(path, '/', ' '), '')
  ) gin_trgm_ops
);

------------------------------ codeblocks ------------------------------
-- table
create table gist_codeblocks (
  hash text primary key,
  code text[],
  code_flat text
);

-- index
create index idx_gist_codeblocks_code_flat_trgm on gist_codeblocks using gin (code_flat gin_trgm_ops);

create index idx_gist_codeblocks_code_flat_fts on gist_codeblocks using gin (to_tsvector('english', code_flat));

-------------------------- snippet - codeblocks --------------------------
-- table
create table snippet_codeblocks_hash_map (
  snippet_id integer references gist_snippets (id),
  codeblock_hash text references gist_codeblocks (hash)
);

-------------------------- blocksDb --------------------------
create table blocks (
  id serial primary key,
  type text not null,
  lang text,
  lines text[] not null
)
----------------------------------------------------
-- create index idx_gist_snippets_path on gist_snippets (path);
-- create index idx_gist_snippets_code_flat_trgm on gist_snippets using gin (code_flat gin_trgm_ops);
-- create index idx_gist_snippets_code_flat_fts on gist_snippets using gin (to_tsvector('simple', coalesce(code_flat, '')));
-- create index idx_gist_snippets_text_flat_fts on gist_snippets using gin (to_tsvector('english', coalesce(code_flat, '')));
----------------------------------------------------
-- create index idx_gist_snippets_text_fts on gist_snippets using gin (to_tsvector('simple', coalesce(text, '')));
-- comment on table gist_snippets is '';
comment on column gist_snippets.path is 'Concatenated words joined with "/" (e.g. section/subsection); used with replace(path, ''/'', '' '') for FTS/trigram';

-- comment on column gist_snippets.title is '';
-- comment on column gist_snippets.code is '';
-- comment on column gist_snippets.text is '';
------------------------------ query helpers ------------------------------
-- Normalized text used for FTS/trigram on snippets (text_flat + path as words).
create or replace function snippet_searchable_text (p_text_flat text, p_path text) returns text as $$
  select coalesce(p_text_flat, '') || ' ' || coalesce(replace(p_path, '/', ' '), '');
$$ language sql immutable;

-- Expand snippet code_hash to code arrays (order preserved). Used by snippet search queries.
create or replace function expand_code_hashes (p_code_hash text[]) returns text[] [] as $$
  select coalesce(
    array_agg(gc.code order by g.ord),
    array[]::text[][]
  )
  from generate_series(1, coalesce(cardinality(p_code_hash), 0)) as g(ord)
  join gist_codeblocks gc on gc.hash = p_code_hash[g.ord];
$$ language sql stable;

-- Build the standard search result row (id, title, tags, description, snippets) from snippet columns.
-- Builds one result row: (id, title, tags, description, snippets).
-- Input: snippet id/title/path, optional text blocks (p_text), code blocks (p_code_array).
-- Output: tags from path (split on '/'), description = single text block if exactly one else null,
--         snippets = merged list of text lines + all code lines (or empty if that one text became description).
create or replace function snippet_search_result_row (
  p_id integer,
  p_title text,
  p_path text,
  p_text text[],
  p_code_array text[] []
) returns table (
  id integer,
  title text,
  tags text[],
  description text,
  snippets text[]
) as $$
  with
  -- Ensure we always have a 2D array. expand_code_hashes can return 1D text[] when there is only one block.
  normalized as (
    select case
      when p_code_array is null then array[]::text[][]
      when array_ndims(p_code_array) = 1 then array[coalesce(p_code_array, array[]::text[])]::text[][]
      else p_code_array
    end as code_2d
  ),
  -- Flatten code_2d to a single text[]: all code lines in order (row-major). unnest(2D) gives one row per element.
  code_flat as (
    select coalesce(
      (
        select array_agg(line order by ord)
        from unnest((select code_2d from normalized)) with ordinality as t(line, ord)
      ),
      array[]::text[]
    ) as arr
  )
  select
    p_id,
    p_title,
    string_to_array(p_path, '/'),   -- tags: path like "a/b/c" -> {'a','b','c'}
    case when cardinality(p_text) = 1 then p_text[1] else null end,   -- description: only if exactly one text block
    case when cardinality(p_text) = 1 then array[]::text[]
      else coalesce(p_text, array[]::text[]) || (select arr from code_flat)   -- snippets: text lines then code lines
    end
  from code_flat;
$$ language sql immutable;
