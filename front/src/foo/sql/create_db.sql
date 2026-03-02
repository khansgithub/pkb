create extension if not exists pg_trgm;
------------------------------ snippets ------------------------------
-- table
create table gist_snippets (
  id         serial primary key,
  path       text not null,
  title      text not null unique,
  -- code       text[][] null,
  -- code_flat  text null,
  text       text[],
  text_flat  text,
  created_at timestamptz default now(),
  code_hash  text[]

  -- constraint at_least_one_content check (
	-- code is not null or text is not null
  -- )
);

create index idx_gist_snippets_text_flat_path on gist_snippets using gin (
  to_tsvector('english', coalesce(text_flat, '') || ' ' || coalesce(path, ''))
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
create index idx_gist_codeblocks_code_flat_fts  on gist_codeblocks using gin (to_tsvector('english', code_flat));
-------------------------- snippet - codeblocks --------------------------
-- table
create table snippet_codeblocks_hash_map (
  snippet_id integer references gist_snippets(id),
  codeblock_hash text references gist_codeblocks(hash)
);


----------------------------------------------------
-- create index idx_gist_snippets_path on gist_snippets (path);
-- create index idx_gist_snippets_code_flat_trgm on gist_snippets using gin (code_flat gin_trgm_ops);
-- create index idx_gist_snippets_code_flat_fts on gist_snippets using gin (to_tsvector('simple', coalesce(code_flat, '')));
-- create index idx_gist_snippets_text_flat_fts on gist_snippets using gin (to_tsvector('english', coalesce(code_flat, '')));
----------------------------------------------------


-- create index idx_gist_snippets_text_fts on gist_snippets using gin (to_tsvector('simple', coalesce(text, '')));
-- comment on table gist_snippets is '';
-- comment on column gist_snippets.path is '';
-- comment on column gist_snippets.title is '';
-- comment on column gist_snippets.code is '';
-- comment on column gist_snippets.text is '';
