# DECISIONS.md

1. **Indexes.**
   - `employees`: `{ emp_code: 1 }` (unique; guarantees employee ID uniqueness and fast lookups) and `{ department: 1, joined_on: 1 }` (serves department filtering, monthly summary, and trend queries).
   - `attendance_logs`: `{ emp_code: 1, date: 1 }` (unique; natural key, punch-in race safety, and regularization), `{ emp_code: 1, punch_in: -1 }` (enables fast punch-out lookup), `{ date: -1, emp_code: 1 }` (backs date filtering and attendance listing order), and `{ date: 1, late_minutes: -1, emp_code: 1 }` (powers the late leaderboard pipeline).
   - *Rejected:* An index on `status` (low cardinality yields poor selectivity) and an index on `email` (no endpoint queries by email).

2. **Punch-in race.**
   Both requests validate and resolve the same attendance date. Both issue an atomic `insert_one`. MongoDB serializes the compound unique index insertion: the first request succeeds and returns 201 Created. The second triggers a `DuplicateKeyError` (code 11000) on `(emp_code, date)`, which our API catches and returns as 409 Conflict.

3. **Ties.**
   Our pipeline uses MongoDB's `$setWindowFields` with standard competition ranking (`$rank: {}`). Because `limit` is applied after ranking (`rank <= limit`), both tied employees share the cutoff rank and are returned (e.g., 11 rows for limit 10), ordered secondarily by `emp_code` ascending.

4. **Headcount.**
   The aggregation pipeline starts from `employees` (matching `joined_on <= month_end`), groups by department to calculate the exact headcount, and then performs a `$lookup` to join `attendance_logs`. Employees with zero logs still contribute to the department's headcount, while contributing 0 to presence totals.

5. **One thing you would change for 100x data.**
   Pre-aggregate daily and monthly statistics asynchronously using MongoDB change streams or a background worker into dedicated summary collections (`daily_department_stats`, `monthly_employee_stats`), avoiding on-demand cross-collection aggregations over 10M+ documents.
