CREATE TABLE IF NOT EXISTS rank_rows (
    id BIGSERIAL PRIMARY KEY,

    dataset TEXT NOT NULL,          -- murmansk / moscow / ...
    metric  TEXT NOT NULL,          -- warmest / coldest / wettest / driest
    scale   TEXT NOT NULL,          -- monthly / decadal
    month   SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    period  TEXT NOT NULL,          -- "M" или "1D"/"2D"/"3D"
    rank    SMALLINT NOT NULL,      -- 1..10 (или сколько есть)
    value   DOUBLE PRECISION NOT NULL,
    year    INTEGER,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_rank_rows_lookup
ON rank_rows(dataset, metric, scale, month, period);