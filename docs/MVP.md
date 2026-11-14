# MVP: The 8–10 conventions for v0.1.0

Fill in one row per convention. The `source` column must cite ISDA or ICMA. The `status` column starts as `TODO`.

| # | convention_id | type | source | status |
|---|---------------|------|--------|--------|
| 1 | `ACT/360` | day_count | ISDA 2006 Definitions, Section 4.16(b) | ✅ seeded |
| 2 | `ACT/365` | day_count | ISDA 2006 Definitions, Section 4.16(b) | TODO |
| 3 | `30/360` | day_count | ISDA 2006 Definitions, Section 4.16(f) | TODO |
| 4 | `30E/360` | day_count | ISDA 2006 Definitions, Section 4.16(g) | TODO |
| 5 | `ACT/ACT` (ISDA) | day_count | ISDA 2006 Definitions, Section 4.16(c) | TODO |
| 6 | `FOLLOWING` | business_day | ISDA 2006 Definitions, Section 4.12 | TODO |
| 7 | `MODIFIED_FOLLOWING` | business_day | ISDA 2006 Definitions, Section 4.12 | TODO |
| 8 | `PRECEDING` | business_day | ISDA 2006 Definitions, Section 4.12 | TODO |
| 9 | `EOM` | roll | ISDA 2006 Definitions, Section 4.13 | TODO |
| 10 | `IMM` | roll | ISDA 2006 Definitions, Section 4.13 | TODO |

## The selection rule

Each convention is selected because (a) it appears in ISDA 2006 Definitions, (b) it is implemented differently in at least two major quant libraries, and (c) a backtest or a trade settlement would produce a different number if it were used incorrectly.

## What is out of scope for v0.1.0

- Holiday calendars. The business day conventions accept a `calendar_id` argument, but the holiday data itself comes from Exchange Calendar (a separate registry).
- Frequency conventions. The schema reserves a `frequencies` array, but no entries ship in v0.1.0.
- Non-ISDA conventions (e.g., `ACT/365L`, `NL/365`). The schema allows them; the MVP does not ship them.
