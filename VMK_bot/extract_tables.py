"""Script to extract tables from pdf to json"""

from .pdf_parser import Parser
import glob
from .database import Database
import hashlib


def setup():
    db = Database()
    db.connect()

    for pdf_table in glob.glob("schedule_tables/*.pdf"):
        print(f"Getting data from {pdf_table}")
        with open(pdf_table, "rb") as f:
            my_hash = hashlib.md5(f.read()).hexdigest()
        if not db.add_hash(my_hash):
            print(f"no {my_hash} in db")
            Parser.import_schedule_to_database(pdf_table)


if __name__ == '__main__':
    setup()
