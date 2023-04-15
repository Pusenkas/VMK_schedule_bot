"""Script to extract tables from pdf to json"""

from pdf_parser import Parser
import glob
from database import Database
import hashlib

if __name__ == '__main__':
    db = Database()
    db.connect()

    for pdf_table in glob.glob("schedule_tables/*.pdf"):
        print(f"Getting data from {pdf_table}")
        my_hash = hashlib.md5(pdf_table.encode()).hexdigest()
        if not db.add_hash(my_hash):
            print(f"no {my_hash} in db")
            Parser.import_schedule_to_database(pdf_table)
