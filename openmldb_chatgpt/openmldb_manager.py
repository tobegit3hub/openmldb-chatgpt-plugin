# Copyright 2023
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openmldb.dbapi import connect
from openmldb.dbapi import DatabaseError
from tabulate import tabulate

from print_util import PrintUtil
from sql_util import SqlUtil


class OpenmldbManager:

    def __init__(self, zk_cluster: str, zk_root_path: str):
        # Connect with zk
        self.connection = connect(zk=zk_cluster, zkPath=zk_root_path)
        self.cursor = self.connection.cursor()

        # Record the last SQL and error message, which may be used by GTP model to analyse
        self.last_sql = None
        self.last_sql_error_message = None

    def get_database_names(self):
        self.cursor.execute("SHOW DATABASES")
        rows = self.cursor.fetchall()
        database_names = [item[0] for item in rows]
        return database_names

    def get_all_table_info(self, database_names: list[str]) -> str:
        """ Example string:
        # db1.t1 (col1)
        # school.student (id, name, age)
        # school.teacher (id, name, subject)
        # fin_tect.bank (id, name, department_id)
        # fin_tect.user (id, name, address）
        # fin_tect.trade (id, employee_id, amount, date)
        """
        table_name_columns_attributes = ""

        for database_name in database_names:
            self.cursor.execute(f"USE {database_name}")
            self.cursor.execute("SHOW TABLES")
            rows = self.cursor.fetchall()
            table_names = [item[0] for item in rows]
            for table_name in table_names:
                self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
                column_names = [description[0] for description in self.cursor.description]
                schema_string = ",".join(column_names)
                table_name_columns_attributes += f"# {database_name}.{table_name} ({schema_string})"

            return table_name_columns_attributes

    def run_openmldb_sql(self, sql) -> bool:
        """
        Run the OpenMLDB SQL.

        :return true if it is successful and false if it fails
        """

        self.last_sql = sql

        try:
            # Run OpenMLDB SQL
            self.cursor.execute(sql)

            if SqlUtil.is_dql(sql):
                PrintUtil.openmldb_print("Success to execute query SQL.")

                rows = self.cursor.fetchall()
                schema = [description[0] for description in self.cursor.description]

                if SqlUtil.is_show_joblog(sql):
                    # Only show the job data
                    print(rows[0][0])
                else:
                    # Show to data as table
                    table_string = tabulate(rows, headers=schema, tablefmt='grid')
                    print(table_string)

            else:
                # Print one line message for DML/DDL
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
