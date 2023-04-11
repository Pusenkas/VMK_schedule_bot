"""Script to extract tables from pdf to json"""

from pdf_parser import Parser
import glob


if __name__ == '__main__':
    for pdf_table in glob.glob("schedule_tables/*.pdf"):
        print(f"Getting data from {pdf_table}")
        Parser.import_schedule_to_database(pdf_table)
