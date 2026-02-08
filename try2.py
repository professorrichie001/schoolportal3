import sqlite3

DB_NAME = "manager.db"

def clear_tables():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Delete all records
        cursor.execute("DELETE FROM logins;")
        cursor.execute("DELETE FROM manager;")

        
        
        conn.commit()
        print("✅ All data cleared from logins and managers tables.")

    except sqlite3.Error as e:
        print("❌ Database error:", e)

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    confirm = input(
        "⚠️ This will permanently delete ALL data from logins and managers tables.\n"
        "Type YES to continue: "
    )

    if confirm == "YES":
        clear_tables()
    else:
        print("❎ Operation cancelled.")
