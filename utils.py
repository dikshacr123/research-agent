def detect_conflicts(web_results, news, wiki, financials):
    """Very simple heuristics to find conflicts across sources.
    Returns a list of strings describing conflicts (best-effort)."""
    conflicts = []
    if financials and financials.get('employees'):
        emp = financials.get('employees')
        for r in (web_results or []):
            body = (r.get('body') or "").lower()
            if 'employee' in body:
                if str(emp) not in body:
                    conflicts.append(f"Employees: yfinance shows {emp}, but web snippet does not match or mentions a different numbers")