#!/bin/sh
set -e

echo "Seeding rank_rows from /ranks/**/*.jsonl ..."

# ВАЖНО: psql должен подключаться к нужной БД
export PGPASSWORD="$POSTGRES_PASSWORD"

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
CREATE TABLE IF NOT EXISTS tmp_rank_jsonl (
  line text NOT NULL
);
TRUNCATE tmp_rank_jsonl;
SQL

# грузим все jsonl в tmp_rank_jsonl
for f in $(find /ranks -type f -name "*.jsonl" | sort); do
  echo "  loading: $f"
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\copy tmp_rank_jsonl(line) FROM '$f';"
done

# переносим в rank_rows
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
INSERT INTO rank_rows(dataset, metric, scale, month, period, rank, value, year)
SELECT
  (obj->>'dataset')::text,
  (obj->>'metric')::text,
  (obj->>'scale')::text,
  (obj->>'month')::int,
  (obj->>'period')::text,
  (obj->>'rank')::int,
  (obj->>'value')::double precision,
  (obj->>'year')::int
FROM (
  SELECT line::jsonb AS obj
  FROM tmp_rank_jsonl
  WHERE line IS NOT NULL AND btrim(line) <> ''
) s;
SQL

echo "Done seeding rank_rows."
