import psycopg
from config import DB_URI
from psycopg.rows import dict_row, tuple_row


#========================================
#   DATABASE QUERY HELPER
#========================================

def get_con(row_factory = dict_row):
    con = psycopg.connect(DB_URI, row_factory = row_factory)
    return con

def sql(
        query: str, 
        params: list | dict | None = None,
        as_dict: bool = True,
        fetch_all = False
    ):
    row_factory = dict_row if as_dict else tuple_row
    with psycopg.connect(DB_URI, row_factory = row_factory) as con:
        with con.cursor() as cursor:
            try:
                if params is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, params)
            except psycopg.DatabaseError as e:
                print(f'Database error: {e}')
                return  
            except Exception as e:
                print(e)
                return
            
            # return results for statements returning results
            if cursor.description is not None:
                return cursor.fetchall() if fetch_all else cursor.fetchone()
            
            return cursor.rowcount
 
    

