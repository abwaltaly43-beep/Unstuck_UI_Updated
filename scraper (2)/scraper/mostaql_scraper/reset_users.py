"""
UNSTUCK APP - Database Reset Script
Clears old test users and OTP verifications across:
1. PostgreSQL (Local / Docker)
2. SQLite (unstuck_auth.db)
3. Supabase Cloud (Profiles)
"""

import os
import shutil
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "unstuck_auth.db")
BACKUP_PATH = os.path.join(ROOT_DIR, f"unstuck_auth.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

load_dotenv(os.path.join(ROOT_DIR, ".env"))

def reset_postgres_users():
    print("=" * 60)
    print("🐘 1. Resetting PostgreSQL Auth Tables (users, otp_verifications)")
    print("=" * 60)
    try:
        from scrapers.database import get_db_cursor
        with get_db_cursor(commit=True) as cur:
            cur.execute("DELETE FROM users;")
            cur.execute("DELETE FROM otp_verifications;")
            print("  ✓ Cleared table: users")
            print("  ✓ Cleared table: otp_verifications")
        print("✅ PostgreSQL users cleared successfully!\n")
    except Exception as e:
        print(f"⚠️  PostgreSQL reset error (might be offline): {e}\n")

def reset_local_auth_db():
    print("=" * 60)
    print("🧹 2. Resetting Local SQLite Auth Database (unstuck_auth.db)")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"⚠️  Database file not found at {DB_PATH}")
        return

    # 1. Create a safe backup first
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"💾 Backup successfully saved to:\n   {BACKUP_PATH}")

    # 2. Clear tables
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = ["users", "otp_verifications", "user_profiles"]
    for tbl in tables:
        try:
            cur.execute(f"DELETE FROM {tbl};")
            cur.execute(f"DELETE FROM sqlite_sequence WHERE name='{tbl}';")
            print(f"  ✓ Cleared table: {tbl}")
        except Exception as e:
            print(f"  ✗ Error clearing {tbl}: {e}")

    conn.commit()
    conn.close()
    print("✅ Local SQLite users cleared successfully!\n")

def reset_supabase_profiles(keep_demo_leaderboard=True):
    print("=" * 60)
    print("☁️  3. Resetting Supabase Profiles & Applications")
    print("=" * 60)

    try:
        from scrapers.supabase_client import get_supabase, is_supabase_configured
        if not is_supabase_configured():
            print("ℹ️  Supabase is not configured or offline. Skipping cloud reset.")
            return

        client = get_supabase()
        if not client:
            print("⚠️  Could not connect to Supabase.")
            return

        demo_emails = [
            "ahmed.fathy.dev@gmail.com",
            "sarah.uiux@unstuck.app",
            "kareem.cloud@unstuck.app",
            "layla.nlp@unstuck.app",
            "omar.flutter@unstuck.app"
        ]

        # 1. Clear user applications
        try:
            client.table("user_applications").delete().neq("id", 0).execute()
            print("  ✓ Cleared table: user_applications")
        except Exception as e:
            print(f"  ✗ Error clearing user_applications: {e}")

        # 2. Clear profiles
        try:
            if keep_demo_leaderboard:
                res = client.table("profiles").select("email").execute()
                all_profiles = res.data or []
                deleted = 0
                for p in all_profiles:
                    em = p.get("email")
                    if em not in demo_emails:
                        client.table("profiles").delete().eq("email", em).execute()
                        deleted += 1
                print(f"  ✓ Deleted {deleted} test profiles from Supabase (Preserved top 5 demo users for Leaderboard).")
            else:
                client.table("profiles").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                print("  ✓ Cleared all profiles from Supabase.")
        except Exception as e:
            print(f"  ✗ Error clearing profiles: {e}")

        print("✅ Supabase reset completed successfully!\n")

    except Exception as e:
        print(f"⚠️  Supabase reset error: {e}")

if __name__ == "__main__":
    reset_postgres_users()
    reset_local_auth_db()
    reset_supabase_profiles(keep_demo_leaderboard=True)
    print("=" * 60)
    print("🎉 ALL DONE! You can now register fresh new accounts.")
    print("=" * 60)
