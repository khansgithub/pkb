drop table if exists temp_snippets CASCADE;
drop table if exists temp_blocks CASCADE;

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

-- 1) insert data into 'temp_snippets' and 'temp_blocks' manually via the gui


-- 2) populate 'snippets'
insert into snippets(id, title, tags, description)
select * from temp_snippets;

-- 3) then populate 'blocks'
WITH a AS (
    SELECT 
        id AS snippet_id, 
        ROW_NUMBER() OVER () AS snippet_idx
    FROM temp_snippets
    LIMIT 20
)
insert into blocks(type, lang,lines, snippet_id, pos)
SELECT type,lang,lines,a.snippet_id,pos
FROM temp_blocks tb
JOIN a 
    ON tb.snippet_idx = a.snippet_idx;