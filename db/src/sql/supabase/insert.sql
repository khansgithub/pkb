WITH
  new_snippets AS (
    INSERT INTO
      snippets (title, tags, description)
    VALUES
      ('redis', '{redis}', ''),
      ('list keys', '{redis}', ''),
      ('read stream', '{redis}', ''),
      ('find keys and pipe to delete', '{redis}', '')
    RETURNING
      id AS snippet_id
  ),
  blocks_to_insert AS (
    SELECT
      *
    FROM
      (
        VALUES
          ('code', 'bas', ARRAY['redis-cli'], 1),
          ('code', 'ba', ARRAY['keys *'], 1),
          ('code', 'b', ARRAY['xrange <key> - +'], 1),
          (
            'code',
            'bashh',
            ARRAY[
              '#             < query >',
              'redis-cli keys rq:res* | awk ''{print $1}'' | xargs redis-cli del'
            ],
            1
          )
      ) AS b (type, lang, lines, pos)
  ),
  numbered_snippets AS (
    SELECT
      snippet_id,
      ROW_NUMBER() OVER () AS rn
    FROM
      new_snippets
  ),
  numbered_blocks AS (
    SELECT
      type,
      lang,
      lines,
      pos,
      ROW_NUMBER() OVER () AS rn
    FROM
      blocks_to_insert
  )
INSERT INTO
  blocks (type, lang, lines, pos, snippet_id)
SELECT
  nb.type::block_type,
  nb.lang,
  nb.lines,
  nb.pos,
  ns.snippet_id
FROM
  numbered_snippets ns
  JOIN numbered_blocks nb USING (rn);
