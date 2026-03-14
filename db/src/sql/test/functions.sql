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
  from generate_series(1, coalesce(cardinality(p_code_hash), 0)) as g (ord)
  join gist_codeblocks gc on gc.hash = p_code_hash[g.ord];
$$ language sql stable;

-- Build the standard search result row (id, title, tags, description, snippets) from snippet columns.
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
  select
    p_id,
    p_title,
    string_to_array(p_path, '/'),
    case when cardinality(p_text) = 1 then p_text[1] else null end,
    case when cardinality(p_text) = 1 then array[]::text[]
      else coalesce(p_text, array[]::text[]) || coalesce(
        (
          select array_agg(p_code_array[t.ord1][u.ord2] order by t.ord1, u.ord2)
          from generate_series(1, coalesce(array_upper((p_code_array)::text[][], 1), 0)) as t(ord1)
          cross join lateral generate_series(1, coalesce(array_upper((p_code_array[t.ord1])::text[], 1), 0)) as u(ord2)
        ),
        array[]::text[]
      )
    end;
$$ language sql immutable;
