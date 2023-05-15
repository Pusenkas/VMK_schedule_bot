"""Main for module."""

from . import server
from . import extract_tables

if __name__ == '__main__':
    extract_tables.setup()
    server.run_server()
