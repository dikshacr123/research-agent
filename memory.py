import json
from pathlib import Path

DB_FILE = Path("assets/sample_output.json")

if not DB_FILE.exists():
    DB_FILE.write_text("{}")  # initialize empty json


def _load_db():
    text = DB_FILE.read_text().strip()
    
    if not text:
        return {}  # file empty → return empty dict

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # fallback if file corrupted
        DB_FILE.write_text("{}")
        return {}


def _save_db(db):
    DB_FILE.write_text(json.dumps(db, indent=2))


def save_plan(company, plan_text):
    db = _load_db()
    db[company] = plan_text
    _save_db(db)


def load_plan(company):
    db = _load_db()
    return db.get(company)


def list_saved_companies():
    db = _load_db()
    return list(db.keys())


def update_plan_section(company, section_heading, new_content):
    db = _load_db()
    plan = db.get(company)

    if not plan:
        return False

    # plan is a dict → update directly
    if section_heading not in plan:
        return False

    plan[section_heading] = new_content
    db[company] = plan
    _save_db(db)
    return True
