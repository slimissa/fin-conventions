-- fin-conventions, generated from fin-conventions.json
-- version: 0.0.1

BEGIN;

DROP TABLE IF EXISTS conventions;
CREATE TABLE conventions (
    convention_id  TEXT PRIMARY KEY,
    type           TEXT NOT NULL,
    name           TEXT NOT NULL,
    description    TEXT NOT NULL,
    formula        TEXT NOT NULL,
    source_url     TEXT NOT NULL
);

INSERT INTO conventions VALUES ('ACT/360', 'day_count', 'Actual/360', 'Actual days in the period divided by a 360-day year.', 'actual_days / 360', 'https://www.isda.org/a/FmwDE/ISDA-2006-Definitions.pdf');

COMMIT;
