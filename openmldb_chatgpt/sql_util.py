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

import re


class SqlUtil:

    @staticmethod
    def autocomplete_keywords():
        # words = ['SELECT', 'INSERT', 'LOAD', 'CREATE DATABASE', 'CREATE TABLE', 'FROM']
        # sql_keyword_string = "SELECT, FROM, WHERE, AND, OR, NOT, ORDER BY, GROUP BY, HAVING, DISTINCT, COUNT, SUM, AVG, MAX, MIN, INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, CROSS JOIN, ON, AS, IN, BETWEEN, LIKE, LIMIT, OFFSET, UNION, UNION ALL, INSERT INTO, VALUES, UPDATE, SET, DELETE, CREATE DATABASE, DROP DATABASE, CREATE TABLE, DROP TABLE, ALTER TABLE, ADD, DROP, MODIFY, CONSTRAINT, PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE, DEFAULT, NULL, NOT NULL, INDEX, AUTO_INCREMENT, COMMIT, ROLLBACK, TRANSACTION, GRANT, REVOKE, TRUNCATE, SHOW, JOB, JOBS, LOG, LAST JOIN, INTO, OUTFILE, @@execute_mode='online', @@execute_mode='offline'"
        # work

        sql_keyword_string = "SELECT, FROM, USE, WHERE, AND, OR, NOT, ORDER BY, GROUP BY, HAVING, COUNT, SUM, AVG, MAX, MIN, ON, AS, IN, BETWEEN, LIKE, LIMIT, UNION, UNION ALL, INSERT INTO, VALUES, UPDATE, SET, DELETE, CREATE DATABASE, DROP DATABASE, CREATE TABLE, DROP TABLE, ADD, DROP,  DEFAULT, NULL, NOT NULL, SHOW, JOB, JOBS, LOG, LAST JOIN, INTO, OUTFILE"
        # sql_keywords = map(str.strip, sql_keyword_string.split(","))
        # TODO: too much and not work
        sql_keywords = ['SELECT', 'INSERT', 'LOAD', 'CREATE DATABASE', 'CREATE TABLE', 'FROM']
        return sql_keywords

    @staticmethod
    def is_possible_sql(text: str) -> bool:
        # Check if the text contains only English letters, digits, whitespace, and punctuation
        pattern = r'^[A-Za-z0-9\s\.*,;:!?\'"(){}\[\]+\-_]*$'
        if not bool(re.match(pattern, text)):
            return False

        text = re.sub(r'--.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        text = text.strip()

        # Check for common SQL keywords
        keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'GRANT', 'REVOKE',
                    'SHOW', 'LOAD', 'SET', 'USE']
        return any([text.upper().startswith(keyword) for keyword in keywords])

    @staticmethod
    def is_dql(sql: str) -> bool:
        sql_keyword = sql.split()[0].upper()
        if sql_keyword in ["SELECT", "SHOW"]:
            return True
        else:
            return False

    @staticmethod
    def is_show_joblog(sql: str) -> bool:
        if sql.lower().startswith("show joblog"):
            return True
        else:
            return False
