import os
import sqlite3


def main():
    sq_path = "Database/data.db"
    con_sql = sqlite3.connect(sq_path)
    cur = con_sql.cursor()
    result = cur.execute("Select * from time").fetchall()
    con_sql.commit()

    return result[:]