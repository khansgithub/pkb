create extension if not exists pg_trgm;
------------------------------ snippets ------------------------------
-- table
create table if not exists gist_snippets (
  id         serial primary key,
  path       text not null,
  title      text not null unique,
  text       text[],
  text_flat  text,
  created_at timestamptz default now(),
  code_hash  text[]
);

CREATE INDEX if not exists idx_gist_snippets_fts
ON gist_snippets
USING gin (
  to_tsvector(
    'simple',
    coalesce(text_flat, '') || ' ' ||
    coalesce(replace(path, '/', ' '), '')
  )
);

create index if not exists idx_gist_snippets_text_flat_path_trgm 
on gist_snippets 
using gin (
  (
    coalesce(text_flat, '') || ' ' ||
    coalesce(replace(path, '/', ' '), '')
  )
  gin_trgm_ops
);
------------------------------ codeblocks ------------------------------
-- table
create table if not exists gist_codeblocks (
  hash text primary key,
  code text[],
  code_flat text
);

-- index
create index if not exists idx_gist_codeblocks_code_flat_trgm
on gist_codeblocks
using gin (code_flat gin_trgm_ops);

create index if not exists idx_gist_codeblocks_code_flat_fts
on gist_codeblocks
using gin (to_tsvector('english', code_flat));
-------------------------- snippet - codeblocks --------------------------
-- table
create table if not exists snippet_codeblocks_hash_map (
  snippet_id integer references gist_snippets(id),
  codeblock_hash text references gist_codeblocks(hash)
);


------------------------------

-- CREATE TABLE numbers (
--     n INT
-- );