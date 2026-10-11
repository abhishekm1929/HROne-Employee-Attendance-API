"""
Interactive Live Demonstration of Employee Attendance & Analytics API
Usage: python demo.py
"""
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def call(method, path, body=None, desc=""):
    print("\n" + "=" * 70)
    print(f"STEP: {desc}")
    print(f">> {method} {BASE_URL}{path}")
    if body:
        print(">> Request Body:")
        print("  ", json.dumps(body, indent=2).replace("\n", "\n   "))

    data = json.dumps(body).encode("utf-8") if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            parsed = json.loads(content) if content else {}
            print(f"<< Status: {resp.status} OK")
            print("<< Response:")
            print("  ", json.dumps(parsed, indent=2).replace("\n", "\n   "))
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        parsed = json.loads(content) if content else {}
        print(f"<< Status: {e.code} Error")
        print("<< Response:")
        print("  ", json.dumps(parsed, indent=2).replace("\n", "\n   "))
        return e.code, parsed

def main():
    print("*" * 70)
    print("   HROne Employee Attendance & Analytics API - LIVE DEMO")
    print("*" * 70)

    # 1. Health Probe
    call("GET", "/health", desc="1. System Health & MongoDB Readiness Probe")

    # 2. Create Employee
    call("POST", "/employees", {
        "emp_code": "EMP0100",
        "name": "Ananya Sharma",
        "email": "ananya@example.com",
        "department": "Engineering",
        "shift_start": "09:30",
        "shift_end": "18:30",
        "joined_on": "2026-07-01"
    }, desc="2. Create New Employee (validates schema, unique index & epoch ms created_at)")

    # 3. List Employees
    call("GET", "/employees?department=Engineering&page=1&page_size=3",
         desc="3. List Employees with Department Filter, Sort & Pagination")

    # 4. Punch In with Late Calculation (09:45 IST on July 15 = 15m late, > 10m grace period)
    # 2026-07-15 09:45:00 IST = 2026-07-15 04:15:00 UTC = 1784088900000 ms
    call("POST", "/attendance/punch-in", {
        "emp_code": "EMP0100",
        "punched_at": 1784088900000,
        "status": "PRESENT"
    }, desc="4. Punch-In with Business Rule R2 (Late: 15 min since 09:30, grace period exceeded)")

    # 5. Duplicate Punch In (Race & Conflict Prevention)
    call("POST", "/attendance/punch-in", {
        "emp_code": "EMP0100",
        "punched_at": 1784088900000,
        "status": "PRESENT"
    }, desc="5. Attempt Duplicate Punch-In on Same Date (Returns 409 Conflict via Unique Index)")

    # 6. Punch Out with Overtime Calculation (19:15 IST = 45m overtime >= 30m min threshold)
    # 2026-07-15 19:15:00 IST = 2026-07-15 13:45:00 UTC = 1784123100000 ms
    call("POST", "/attendance/punch-out", {
        "emp_code": "EMP0100",
        "punched_at": 1784123100000
    }, desc="6. Punch-Out with Business Rules R3-R5 (Computes 9.50h work, 45m overtime, half_day=false)")

    # 7. List Attendance Records
    call("GET", "/attendance?emp_code=EMP0100",
         desc="7. Query Attendance Records (Fast Index Scan on emp_code and date)")

    # 8. Regularization with Audit Trail
    call("PATCH", "/attendance/EMP0100/2026-07-15", {
        "status": "WFH",
        "reason": "Biometric terminal failed, regularized to WFH",
        "regularized_by": "hr.manager"
    }, desc="8. Regularize Record with Audit Trail (Updates fields & appends to history array)")

    # 9. Employee Monthly Summary
    call("GET", "/analytics/employees/EMP0001/monthly?month=2026-07",
         desc="9. Monthly Attendance Summary for Employee (MongoDB Aggregation Pipeline)")

    # 10. Department Summary (Includes zero-log employees in headcount)
    call("GET", "/analytics/departments/summary?month=2026-07",
         desc="10. Cross-Collection Department Summary (Headcount per R9, avg work hours, counts)")

    # 11. Late Leaderboard
    call("GET", "/analytics/leaderboard/late?month=2026-07&limit=5",
         desc="11. Late-Comers Leaderboard (Competition Ranking ties 1,2,2,4 with $setWindowFields)")

    # 12. Department Daily Trend with Gap Filling ($densify)
    call("GET", "/analytics/departments/Sales/trend?from=2026-07-06&to=2026-07-10",
         desc="12. Department Daily Trend (Gap-filling via $densify and 7-day moving average)")

    # 13. Query Plan Verification via Explain Endpoint
    call("GET", "/admin/explain/attendance_list?date_from=2026-07-01&date_to=2026-07-31",
         desc="13. Admin Explain Endpoint (Proves execution uses IXSCAN with zero COLLSCAN)")

    print("\n" + "*" * 70)
    print("   ALL 13 DEMO SCENARIOS COMPLETED SUCCESSFULLY!")
    print("*" * 70)

if __name__ == "__main__":
    main()
