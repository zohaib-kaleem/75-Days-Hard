import sqlite3
import os
from datetime import datetime, timedelta

DB_NAME = "75days.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # User Profile
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT 'User',
            start_date TEXT,
            challenge_duration INTEGER DEFAULT 75
        )
    ''')
    
    # Sections/Categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    
    # Custom Tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT,
            section_id INTEGER,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (section_id) REFERENCES sections(id)
        )
    ''')
    
    # Daily Logs (Modified to store task completion in JSON or a separate table)
    # For simplicity, we'll use a task_completions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_completions (
            date TEXT,
            task_id INTEGER,
            is_done INTEGER DEFAULT 0,
            PRIMARY KEY (date, task_id),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')

    # Seed default sections and tasks
    cursor.execute("INSERT OR IGNORE INTO sections (name) VALUES ('Challenge Rules')")
    cursor.execute("SELECT id FROM sections WHERE name = 'Challenge Rules'")
    section_id = cursor.fetchone()[0]
    
    # Check if this section already has tasks to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE section_id = ?", (section_id,))
    if cursor.fetchone()[0] == 0:
        default_tasks = [
            "Workout 1 (45 mins)", "Workout 2 (45 mins)", "Outdoor Workout", 
            "Follow Diet / No Cheats", "Drink 1 Gallon Water", "Read 10 Pages", "Progress Photo"
        ]
        for task in default_tasks:
            cursor.execute("INSERT INTO tasks (label, section_id) VALUES (?, ?)", (task, section_id))

    # Settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Default settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'dark')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('notifications', 'on')")
    
    conn.commit()
    conn.close()

def get_user_profile():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    return user

def create_user_profile(name, start_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_profile (name, start_date) VALUES (?, ?)", (name, start_date))
    conn.commit()
    conn.close()

def get_log_for_date(date_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_logs WHERE date = ?", (date_str,))
    log = cursor.fetchone()
    conn.close()
    return log

def update_log(date_str, data):
    # data is a dict of column names and values
    conn = get_connection()
    cursor = conn.cursor()
    
    columns = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values())
    values.append(date_str)
    
    # Check if exists
    cursor.execute("SELECT id FROM daily_logs WHERE date = ?", (date_str,))
    if cursor.fetchone():
        cursor.execute(f"UPDATE daily_logs SET {columns} WHERE date = ?", values)
    else:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        cursor.execute(f"INSERT INTO daily_logs (date, {cols}) VALUES (?, {placeholders})", [date_str] + list(data.values()))
    
    conn.commit()
    conn.close()

def get_sections():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sections")
    sections = cursor.fetchall()
    conn.close()
    return sections

def get_tasks_for_section(section_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE section_id = ? AND is_active = 1", (section_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def save_task_completion(date_str, task_id, is_done):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO task_completions (date, task_id, is_done) 
        VALUES (?, ?, ?)
        ON CONFLICT(date, task_id) DO UPDATE SET is_done = excluded.is_done
    ''', (date_str, task_id, is_done))
    conn.commit()
    conn.close()

def get_completions_for_date(date_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, is_done FROM task_completions WHERE date = ?", (date_str,))
    completions = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return completions

def add_task(label, section_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO sections (name) VALUES (?)", (section_name,))
    cursor.execute("SELECT id FROM sections WHERE name = ?", (section_name,))
    section_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO tasks (label, section_id) VALUES (?, ?)", (label, section_id))
    conn.commit()
    conn.close()

def remove_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET is_active = 0 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_completion_stats(start_date_str):
    conn = get_connection()
    cursor = conn.cursor()
    # Get total active tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE is_active = 1")
    total_active_tasks = cursor.fetchone()[0]
    if total_active_tasks == 0: total_active_tasks = 1
    
    # Get completion counts per date since start_date
    cursor.execute('''
        SELECT date, COUNT(*) as done_count 
        FROM task_completions 
        WHERE is_done = 1 AND date >= ?
        GROUP BY date
    ''', (start_date_str,))
    rows = cursor.fetchall()
    
    completed_days = 0
    total_tasks_done = 0
    for date_str, done_count in rows:
        # A day is "complete" if user did all currently active tasks 
        # (This is a simplification, but better than nothing)
        if done_count >= total_active_tasks:
            completed_days += 1
        total_tasks_done += done_count
            
    conn.close()
    return completed_days, total_tasks_done

def get_completion_by_section(start_date_str):
    conn = get_connection()
    cursor = conn.cursor()
    # Join task_completions with tasks and sections, filter by date
    cursor.execute('''
        SELECT s.name, COUNT(tc.task_id) as tasks_done
        FROM sections s
        JOIN tasks t ON s.id = t.section_id
        JOIN task_completions tc ON t.id = tc.task_id
        WHERE tc.is_done = 1 AND tc.date >= ?
        GROUP BY s.name
    ''', (start_date_str,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_streak_info(start_date_str):
    """
    Calculates the current streak. 
    A streak is the number of consecutive days (starting from start_date) 
    where ALL active tasks were completed.
    If a day is missed, the streak resets.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Get total active tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE is_active = 1")
    total_active = cursor.fetchone()[0]
    if total_active == 0: total_active = 1
    
    # 2. Get all completion records grouped by date
    cursor.execute('''
        SELECT date, COUNT(*) as done_count 
        FROM task_completions 
        WHERE is_done = 1 AND date >= ?
        GROUP BY date
        ORDER BY date ASC
    ''', (start_date_str,))
    completions = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 3. Iterate from start_date to yesterday to find the actual streak
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    
    current_streak = 0
    streak_start_date = start_date
    
    # Check every day from challenge start to yesterday
    curr = start_date
    while curr < today:
        d_str = curr.isoformat()
        done = completions.get(d_str, 0)
        
        if done >= total_active:
            current_streak += 1
        else:
            # RESET!
            current_streak = 0
            streak_start_date = curr + timedelta(days=1)
        curr += timedelta(days=1)
        
    # Today's progress doesn't kill the streak yet, but it can increment it
    today_done = completions.get(today.isoformat(), 0)
    if today_done >= total_active:
        is_today_complete = True
    else:
        is_today_complete = False
        
    conn.close()
    # We return the streak count AND the date the current streak started
    return current_streak, streak_start_date.isoformat(), is_today_complete

def get_daily_completion_data(streak_start_date_str):
    """
    Returns a list of (date, percentage) for the current streak.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE is_active = 1")
    total_active = cursor.fetchone()[0]
    if total_active == 0: total_active = 1
    
    cursor.execute('''
        SELECT date, COUNT(*) as done_count 
        FROM task_completions 
        WHERE is_done = 1 AND date >= ?
        GROUP BY date
        ORDER BY date ASC
    ''', (streak_start_date_str,))
    
    rows = cursor.fetchall()
    today = datetime.now().date()
    start_date = datetime.strptime(streak_start_date_str, "%Y-%m-%d").date()
    
    data = []
    curr = start_date
    completion_dict = {row[0]: row[1] for row in rows}
    
    while curr <= today:
        d_str = curr.isoformat()
        done = completion_dict.get(d_str, 0)
        perc = (done / total_active) * 100
        data.append((d_str, perc))
        curr += timedelta(days=1)
        
    conn.close()
    return data

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
