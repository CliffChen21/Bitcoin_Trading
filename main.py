#!/usr/bin/python3
from tools.database_writer import DataBaseWriter
from threading import Timer
import json

if __name__ == "__main__":
    # Scripts to record the ticks into database
    with open("Tokens.json", 'r') as f:
        Tokens = json.load(f)

    db_writer = DataBaseWriter(Tokens=Tokens)
    # db_writer.create_table()

    def exe():
        db_writer.start_record()
        Timer(0, exe).start()

    try:
        exe()
    except Exception as e:
        print(e)