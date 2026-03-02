create table snippetCode(
  id serial primary key,
  code varchar
);

create table snippetsDb(
  id serial primary key,
  snippetIndex serial references snippetCode(id),
  metadata varchar,
  metadataAi varchar
);

select id, text from test where to_tsvector(text) @@ plainto_tsquery('minimise')

insert into snippetCode (code) values
  ('#! /usr/bin/env python\nfrom setuptools import setup\nif __name__ == \"__main__\":\n    setup()'),