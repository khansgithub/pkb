-- Schema for merged_gists.json
--
-- Each object with `code` or `other` becomes a row.
-- The path (e.g. "android.get the SHA1 signature", "python.poetry.pyproject.toml")
-- is stored as a column. When both `code` and `other` exist in the same object,
-- they belong to the same row.

create table gist_snippets (
  id         serial primary key,
  path       text not null unique,
  title      text not null,
  code       text,
  other      text,
  created_at timestamptz default now(),

  constraint at_least_one_content check (
    code is not null or other is not null
  )
);

-- Index for path lookups and prefix searches (e.g. path like 'python.%')
create index idx_gist_snippets_path on gist_snippets (path);

-- Full-text search on code and other
create index idx_gist_snippets_code_fts on gist_snippets using gin (to_tsvector('english', coalesce(code, '')));
create index idx_gist_snippets_other_fts on gist_snippets using gin (to_tsvector('english', coalesce(other, '')));

comment on table gist_snippets is 'Snippets from merged gists; each row = one object with code and/or other content';
comment on column gist_snippets.path is 'Dot-separated path from root (e.g. android.get the SHA1 signature, python.poetry.pyproject.toml)';
comment on column gist_snippets.title is 'Last segment of path (snippet name)';
comment on column gist_snippets.code is 'Code block content, lines joined with newlines';
comment on column gist_snippets.other is 'Misc content (notes, links), lines joined with newlines';
