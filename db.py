import sqlite3

DB_NAME = "financial_stability.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Таблица предприятий
    cur.execute('''
        CREATE TABLE IF NOT EXISTS enterprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT
        )
    ''')

    # Таблица финансовых данных
    cur.execute('''
        CREATE TABLE IF NOT EXISTS financial_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enterprise_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            assets REAL NOT NULL,
            liabilities REAL NOT NULL,
            equity REAL NOT NULL,
            profit REAL NOT NULL,
            revenue REAL NOT NULL,
            current_assets REAL NOT NULL,
            current_liabilities REAL NOT NULL,
            FOREIGN KEY (enterprise_id) REFERENCES enterprises(id)
        )
    ''')

    conn.commit()
    conn.close()

# Добавление нового предприятия
def add_enterprise(name: str, industry: str = ''):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO enterprises (name, industry) VALUES (?, ?)", (name, industry))
    conn.commit()
    conn.close()

# Получение списка предприятий
def get_enterprises():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM enterprises")
    rows = cur.fetchall()
    conn.close()
    return rows

# Добавление финансовых данных
def add_financial_data(enterprise_id: int, period: str, assets: float, liabilities: float,
                       equity: float, profit: float, revenue: float,
                       current_assets: float, current_liabilities: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO financial_data (
            enterprise_id, period, assets, liabilities, equity, profit,
            revenue, current_assets, current_liabilities
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (enterprise_id, period, assets, liabilities, equity, profit, revenue, current_assets, current_liabilities))
    conn.commit()
    conn.close()

# Получение финансовых данных по предприятию
def get_financial_data(enterprise_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT period, assets, liabilities, equity, profit, revenue,
               current_assets, current_liabilities
        FROM financial_data
        WHERE enterprise_id = ?
        ORDER BY period
    ''', (enterprise_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
