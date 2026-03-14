create extension if not exists pg_trgm;

------------------------------ functinos ------------------------------
create or replace function array_to_string_immut (arr text[]) returns text language sql immutable as $$
    select array_to_string(arr, ' ');
$$;

-- types
create type block_type as ENUM('code', 'text');

--tables
create table snippets (
  id integer generated always as identity not null unique primary key,
  title text not null default ''::text,
  tags text[] not null,
  description text not null default ''::text
  -- data_flat text not null
);

create table blocks (
  id integer generated always as identity not null primary key,
  type block_type not null,
  lang text,
  lines text[] not null,
  -- lines_flat text not null,
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
