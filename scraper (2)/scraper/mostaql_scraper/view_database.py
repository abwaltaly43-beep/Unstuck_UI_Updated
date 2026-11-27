"""
UNSTUCK - Visual Database Inspector
Displays all tables and data from PostgreSQL and SQLite.
Generates an interactive HTML dashboard and opens it in the browser.
"""

import os
import sys
import json
import sqlite3
import webbrowser
from datetime import datetime
from dotenv import load_dotenv

# Reconfigure stdout for Windows console UTF-8 support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def inspect_postgresql():
    results = {}
    try:
        from scrapers.database import get_db_cursor
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = [r["table_name"] for r in cur.fetchall()]
            for t in tables:
                # Get columns
                cur.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = '{t}'
                    ORDER BY ordinal_position;
                """)
                columns = [{"name": r["column_name"], "type": r["data_type"]} for r in cur.fetchall()]

                # Count rows
                cur.execute(f"SELECT COUNT(*) FROM {t};")
                row_count = cur.fetchone()["count"]

                # Sample data (up to 15 rows)
                cur.execute(f"SELECT * FROM {t} ORDER BY 1 DESC LIMIT 15;")
                rows = cur.fetchall()
                # Convert RealDictRow to standard dict
                clean_rows = []
                for row in rows:
                    row_dict = {}
                    for k, v in dict(row).items():
                        if isinstance(v, (datetime,)):
                            row_dict[k] = v.isoformat()
                        elif isinstance(v, (dict, list)):
                            row_dict[k] = json.dumps(v, ensure_ascii=False)
                        else:
                            row_dict[k] = str(v) if v is not None else ""
                    clean_rows.append(row_dict)

                results[t] = {
                    "count": row_count,
                    "columns": columns,
                    "sample": clean_rows
                }
    except Exception as e:
        results["_error"] = str(e)
    return results

def inspect_sqlite():
    results = {}
    db_path = os.path.join(ROOT_DIR, "unstuck_auth.db")
    if not os.path.exists(db_path):
        results["_error"] = "unstuck_auth.db not found"
        return results

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cur.fetchall()]

        for t in tables:
            cur.execute(f"PRAGMA table_info({t});")
            columns = [{"name": r[1], "type": r[2]} for r in cur.fetchall()]

            cur.execute(f"SELECT COUNT(*) FROM {t};")
            row_count = cur.fetchone()[0]

            cur.execute(f"SELECT * FROM {t} ORDER BY 1 DESC LIMIT 15;")
            rows = cur.fetchall()
            clean_rows = [dict(r) for r in rows]

            results[t] = {
                "count": row_count,
                "columns": columns,
                "sample": clean_rows
            }
        conn.close()
    except Exception as e:
        results["_error"] = str(e)
    return results

def generate_html_viewer(pg_data, sq_data):
    html_path = os.path.join(ROOT_DIR, "database_viewer.html")

    def build_table_card(t_name, info, db_type):
        count = info.get("count", 0)
        cols = info.get("columns", [])
        sample = info.get("sample", [])

        cols_th = "".join(f"<th>{c['name']}<br><span style='font-size:10px;color:#94a3b8;font-weight:normal;'>{c['type']}</span></th>" for c in cols)
        
        rows_tr = ""
        if sample:
            for row in sample:
                tds = "".join(f"<td title='{str(row.get(c['name'], ''))}'>{str(row.get(c['name'], ''))[:80] + ('...' if len(str(row.get(c['name'], ''))) > 80 else '')}</td>" for c in cols)
                rows_tr += f"<tr>{tds}</tr>"
        else:
            rows_tr = f"<tr><td colspan='{len(cols)}' style='text-align:center;padding:24px;color:#64748b;'>لا توجد بيانات حالياً في هذا الجدول (Empty Table)</td></tr>"

        return f"""
        <div class="table-card" id="{db_type}_{t_name}">
            <div class="table-header">
                <div>
                    <span class="table-name">📁 {t_name}</span>
                    <span class="badge badge-cols">{len(cols)} أعمدة</span>
                </div>
                <div class="badge badge-count">📊 {count} صفوف (Rows)</div>
            </div>
            <div class="table-scroll">
                <table>
                    <thead><tr>{cols_th}</tr></thead>
                    <tbody>{rows_tr}</tbody>
                </table>
            </div>
        </div>
        """

    pg_cards = ""
    if "_error" in pg_data:
        pg_cards = f"<div class='error-box'>⚠️ تعذر الاتصال بـ PostgreSQL: {pg_data['_error']}</div>"
    else:
        for t_name, info in pg_data.items():
            pg_cards += build_table_card(t_name, info, "pg")

    sq_cards = ""
    if "_error" in sq_data:
        sq_cards = f"<div class='error-box'>⚠️ تعذر قراءة SQLite: {sq_data['_error']}</div>"
    else:
        for t_name, info in sq_data.items():
            sq_cards += build_table_card(t_name, info, "sq")

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UNSTUCK - مستعرض قاعدة البيانات</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --primary: #be123c;
            --text: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 30px 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .header h1 {{ font-size: 26px; color: #fff; display: flex; align-items: center; gap: 10px; }}
        .tabs {{ display: flex; gap: 12px; margin-bottom: 25px; }}
        .tab-btn {{
            background: #1e293b;
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 10px 22px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: bold;
            transition: 0.2s;
        }}
        .tab-btn.active {{
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .table-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .table-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #243248;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
        }}
        .table-name {{ font-size: 18px; font-weight: bold; color: #fff; margin-left: 10px; }}
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        .badge-count {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }}
        .badge-cols {{ background: rgba(59, 130, 246, 0.2); color: #3b82f6; }}
        .table-scroll {{ overflow-x: auto; max-height: 400px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            font-size: 13px;
        }}
        th {{
            background: #162032;
            color: #e2e8f0;
            padding: 12px 14px;
            border-bottom: 2px solid var(--border);
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        td {{
            padding: 10px 14px;
            border-bottom: 1px solid #2d3d54;
            color: #cbd5e1;
            white-space: nowrap;
            max-width: 320px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        tr:hover td {{ background: #28374d; }}
        .error-box {{
            background: #451a24;
            color: #f87171;
            border: 1px solid #b91c1c;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐘 مستعرض جداول وقواعد بيانات UNSTUCK</h1>
            <div style="font-size: 13px; color: var(--text-muted);">تم التحديث: {datetime.now().strftime("%Y-%m-%d %I:%M %p")}</div>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('pg')">🐘 PostgreSQL (Local Port 5432)</button>
            <button class="tab-btn" onclick="showTab('sq')">📁 SQLite (unstuck_auth.db)</button>
        </div>

        <div id="tab-pg" class="tab-content active">
            {pg_cards}
        </div>

        <div id="tab-sq" class="tab-content">
            {sq_cards}
        </div>
    </div>

    <script>
        function showTab(type) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            if(type === 'pg') {{
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('tab-pg').classList.add('active');
            }} else {{
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('tab-sq').classList.add('active');
            }}
        }}
    </script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html_path

def main():
    print("=" * 65)
    print("🔍 UNSTUCK DATABASE INSPECTOR")
    print("=" * 65)

    print("\n⏳ 1. Connecting to PostgreSQL (Local Port 5432)...")
    pg_res = inspect_postgresql()
    if "_error" in pg_res:
        print(f"   ⚠️  PostgreSQL error: {pg_res['_error']}")
    else:
        for t, info in pg_res.items():
            print(f"   • {t:<22} -> {info['count']:>5} صفوف (Rows)")

    print("\n⏳ 2. Reading SQLite (unstuck_auth.db)...")
    sq_res = inspect_sqlite()
    if "_error" in sq_res:
        print(f"   ⚠️  SQLite error: {sq_res['_error']}")
    else:
        for t, info in sq_res.items():
            print(f"   • {t:<22} -> {info['count']:>5} صفوف (Rows)")

    print("\n⏳ 3. Generating visual dashboard...")
    viewer_file = generate_html_viewer(pg_res, sq_res)
    print(f"✅ Dashboard generated at:\n   {viewer_file}")

    print("\n🌐 Opening visual dashboard in your browser...")
    webbrowser.open(f"file:///{viewer_file.replace(os.sep, '/')}")
    print("=" * 65)
    print("🎉 Done! Inspect your tables in the opened browser window.")
    print("=" * 65)

if __name__ == "__main__":
    main()
