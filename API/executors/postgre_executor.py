import pg8000
import time
from urllib.parse import urlparse
from premsql.executors.base import BaseExecutor

class PostgreSQLExecutor(BaseExecutor):
    def parse_dsn(self, dsn: str):

        """
            Las credenciales que conectan  ha esta base de datos son de prueba y estan
            colocadas de esta forma por defecto.
        """
        parsed = urlparse(dsn)
        return {
            "user": "admin",
            "password": "gnusolidario",
            "host": "localhost",
            "port": parsed.port or 5432,
            "database": "ghdemo44"
        }

    def execute_sql(self, sql: str, dsn_or_db_path: str) -> dict:
        conn_params = self.parse_dsn(dsn_or_db_path)
        result, error = None, None
        start_time = time.time()
        
        try:
            conn = pg8000.connect(**conn_params)
            cursor = conn.cursor()
            cursor.execute(sql)
            try:
                result = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
            except pg8000.dbapi.ProgrammingError:
                # If no results to fetch (e.g., for INSERT)
                result = None
                column_names = None
            conn.commit()
        except Exception as e:
            error = str(e)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            end_time = time.time()

        return {
            "result": result,
            "columns": column_names,
            "error": error,
            "execution_time": end_time - start_time,
        }
