from psycopg import Connection
from psycopg.rows import TupleRow


type Database = Connection[TupleRow]
