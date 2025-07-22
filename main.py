import sqlite3
import tkinter as tk
from tkinter import filedialog
import zipfile
import os
import shutil

# Unzips a .backup file (which is really just a zip) into a given folder
def extract_backup(backup_path, extract_to):
    with zipfile.ZipFile(backup_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted '{backup_path}' to '{extract_to}'")

# Walks through a folder and finds the song.db file — assumes there's only one
def find_song_db(directory):
    for root, _, files in os.walk(directory):
        if "song.db" in files:
            return os.path.join(root, "song.db")
    raise FileNotFoundError("song.db not found in extracted backup.")

# Zips up a folder and saves it as a .backup file — basically rebranding a zip
def repackage_backup(source_dir, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, source_dir)
                zipf.write(full_path, arcname)
    print(f"Repackaged to '{output_path}'")

# Gets the column names from a table in a SQLite database
def get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]  # row[1] is the column name

# Copies data from one SQLite DB to another, matching columns where possible
def copy_data(source_db, target_db):
    src_conn = sqlite3.connect(source_db)
    tgt_conn = sqlite3.connect(target_db)

    src_cursor = src_conn.cursor()
    tgt_cursor = tgt_conn.cursor()

    # Grab all table names from the source DB
    src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in src_cursor.fetchall()]

    excluded_tables = {"room_master_table"}  # internal SQLite table we don't want to touch
    copied_tables, skipped_tables, errored_tables = [], [], []

    for table in tables:
        if table in excluded_tables:
            print(f"Skipping internal table: {table}")
            skipped_tables.append(table)
            continue

        print(f"\nCopying table: {table}")
        src_columns = get_table_columns(src_cursor, table)
        tgt_columns = get_table_columns(tgt_cursor, table)
        common_columns = [col for col in src_columns if col in tgt_columns]

        if not common_columns:
            print(f"Skipping table '{table}': no matching columns.")
            skipped_tables.append(table)
            continue

        # Escape column names in case they're reserved keywords
        col_list = ', '.join([f'"{col}"' for col in common_columns])
        placeholders = ', '.join(['?'] * len(common_columns))

        try:
            src_cursor.execute(f"SELECT {col_list} FROM {table}")
            rows = src_cursor.fetchall()

            if rows:
                insert_query = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
                tgt_cursor.executemany(insert_query, rows)
                tgt_conn.commit()
                print(f"{len(rows)} rows copied to '{table}'")
                copied_tables.append(table)
            else:
                print(f"No data to copy in '{table}'")
                copied_tables.append(table)

        except Exception as e:
            print(f"Error copying table '{table}': {e}")
            errored_tables.append(table)

    src_conn.close()
    tgt_conn.close()

    # Summary of what happened
    print("\nSummary Report")
    print(f"Tables copied: {len(copied_tables)} → {copied_tables}")
    print(f"Tables skipped: {len(skipped_tables)} → {skipped_tables}")
    print(f"Tables errored: {len(errored_tables)} → {errored_tables}")
    print("\nData copy complete.")

# Main logic — handles file selection, extraction, copying, and repackaging
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Ask user to pick the source .backup file
    print("Select source .backup file...")
    root = tk.Tk()
    root.withdraw()
    source_backup = filedialog.askopenfilename(title="Select Source .backup File", filetypes=[("Backup Files", "*.backup")])
    if not source_backup:
        print("Source file selection cancelled.")
        exit()

    # Define paths for extraction and output
    source_extract_dir = os.path.join(script_dir, "source_extracted")
    target_extract_dir = os.path.join(script_dir, "target_extracted")
    target_backup_path = os.path.join(script_dir, "updated_outertune.backup")
    target_backup_original = os.path.join(script_dir, "empty_outertune.backup")

    # Clean up any old extracted folders
    for d in [source_extract_dir, target_extract_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # Unzip both backup files
    extract_backup(source_backup, source_extract_dir)
    extract_backup(target_backup_original, target_extract_dir)

    # Find the song.db files inside each extracted folder
    source_db = find_song_db(source_extract_dir)
    target_db = find_song_db(target_extract_dir)

    # Copy the data from source to target
    copy_data(source_db, target_db)

    # Zip the updated target folder back into a .backup file
    repackage_backup(target_extract_dir, target_backup_path)
