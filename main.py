import sqlite3
import tkinter as tk
from tkinter import filedialog

def select_db_file(title):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=[("SQLite DB files", "*.db")])

def get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]  # row[1] is column name

def copy_data(source_db, target_db):
    src_conn = sqlite3.connect(source_db)
    tgt_conn = sqlite3.connect(target_db)

    src_cursor = src_conn.cursor()
    tgt_cursor = tgt_conn.cursor()

    # Get all table names from source
    src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in src_cursor.fetchall()]

    excluded_tables = {"room_master_table"}
    copied_tables = []
    skipped_tables = []
    errored_tables = []

    for table in tables:
        if table in excluded_tables:
            print(f"🚫 Skipping internal table: {table}")
            skipped_tables.append(table)
            continue

        print(f"\n🔄 Copying table: {table}")

        src_columns = get_table_columns(src_cursor, table)
        tgt_columns = get_table_columns(tgt_cursor, table)

        common_columns = [col for col in src_columns if col in tgt_columns]

        if not common_columns:
            print(f"⚠️ Skipping table '{table}': no matching columns.")
            skipped_tables.append(table)
            continue

        # Escape column names to handle reserved keywords
        col_list = ', '.join([f'"{col}"' for col in common_columns])
        placeholders = ', '.join(['?'] * len(common_columns))

        try:
            src_cursor.execute(f"SELECT {col_list} FROM {table}")
            rows = src_cursor.fetchall()

            if rows:
                insert_query = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
                tgt_cursor.executemany(insert_query, rows)
                tgt_conn.commit()
                print(f"✅ {len(rows)} rows copied to '{table}'")
                copied_tables.append(table)
            else:
                print(f"ℹ️ No data to copy in '{table}'")
                copied_tables.append(table)

        except Exception as e:
            print(f"❌ Error copying table '{table}': {e}")
            errored_tables.append(table)

    src_conn.close()
    tgt_conn.close()

    # Summary
    print("\n📋 Summary Report")
    print(f"✅ Tables copied: {len(copied_tables)} → {copied_tables}")
    print(f"⚠️ Tables skipped: {len(skipped_tables)} → {skipped_tables}")
    print(f"❌ Tables errored: {len(errored_tables)} → {errored_tables}")

    print("\n✅ Data copy complete.")

if __name__ == "__main__":
    print("Select source database (DB file 1)...")
    source_db = select_db_file("Select Source DB File")
    print("Select destination database (DB file 2)...")
    target_db = select_db_file("Select Destination DB File")

    if source_db and target_db:
        copy_data(source_db, target_db)
    else:
        print("❌ File selection cancelled.")
