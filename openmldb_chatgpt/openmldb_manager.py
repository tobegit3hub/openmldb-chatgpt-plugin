

from openmldb.dbapi import connect
from openmldb.dbapi import DatabaseError
from tabulate import tabulate

from print_util import PrintUtil
from sql_util import SqlUtil


class OpenmldbManager:

    def __init__(self, zk_cluster: str, zk_root_path: str):
        self.connection = connect(zk=zk_cluster, zkPath=zk_root_path)
        self.cursor = self.connection.cursor()

        self.last_sql = None
        self.last_sql_error_message = None

    def run_openmldb_sql(self, sql) -> bool:
        self.last_sql = sql

        try:
            self.cursor.execute(sql)

            if SqlUtil.is_dql(sql):
                PrintUtil.openmldb_print("Success to execute query SQL.")

                rows = self.cursor.fetchall()
                schema = [description[0] for description in self.cursor.description]

                if SqlUtil.is_show_joblog(sql):
                    print(rows[0][0])
                else:
                    # TODO: We may use GPT to analyse output data
                    table_string = tabulate(rows, headers=schema, tablefmt='grid')
                    print(table_string)

            else:
                PrintUtil.openmldb_print(f"Success to execute SQL. Rows affected: {self.cursor.rowcount}")

            return True
        except DatabaseError as e:
            PrintUtil.openmldb_print("Fail to execute SQL and get error message: ")
            PrintUtil.openmldb_print(e.message)
            self.last_sql_error_message = e.message
            return False

    def close(self):
        self.cursor.close()
        self.connection.close()