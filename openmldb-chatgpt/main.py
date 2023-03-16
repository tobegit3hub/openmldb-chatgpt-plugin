#!/usr/bin/env python3

import openai
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from queue import Queue
import configparser
from openmldb.dbapi import connect
from openmldb.dbapi import DatabaseError
from tabulate import tabulate

config = configparser.ConfigParser()
config_directory = os.path.join(os.path.expanduser("~"), ".openmldb/")

if not os.path.exists(config_directory):
    os.makedirs(config_directory)
    # print(f"Directory '{config_directory}' created.")
else:
    pass
    # print(f"Directory '{config_directory}' already exists.")

config_file_path = os.path.join(config_directory, "openmldb-chatgpt.ini")


config = configparser.ConfigParser()
"""
config.add_section("OpenAI")
config.set("OpenAI", "api_key", "xxx")
config.set("OpenAI", "model_engine", "gpt-3.5-turbo")
config.set("OpenAI", "max_tokens", "20")

config.add_section("OpenMLDB")
config.set("OpenMLDB", "zk_cluster", "127.0.0.1:2181")
config.set("OpenMLDB", "zk_root_path", "/openmldb")

# if not os.path.exists(config_file_path):
with open(config_file_path, "w") as config_file:
    config.write(config_file)
"""

# Read the configuration file
config.read(config_file_path)
# print("---------------")
# print(config.get("OpenAI", "api_key"))
# print(config.has_option("OpenAI", "xxx"))


"""    
try:
    with open(config_file_path, "rw") as config_file:
        config_data = config_file.read()
        print(f"Configuration data:\n{config_data}")
except FileNotFoundError:
    print(f"Config file '{config_file_name}' not found in the user's home directory.")
"""

# words = ['SELECT', 'INSERT', 'LOAD', 'CREATE DATABASE', 'CREATE TABLE', 'FROM']
# sql_keyword_string = "SELECT, FROM, WHERE, AND, OR, NOT, ORDER BY, GROUP BY, HAVING, DISTINCT, COUNT, SUM, AVG, MAX, MIN, INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, CROSS JOIN, ON, AS, IN, BETWEEN, LIKE, LIMIT, OFFSET, UNION, UNION ALL, INSERT INTO, VALUES, UPDATE, SET, DELETE, CREATE DATABASE, DROP DATABASE, CREATE TABLE, DROP TABLE, ALTER TABLE, ADD, DROP, MODIFY, CONSTRAINT, PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE, DEFAULT, NULL, NOT NULL, INDEX, AUTO_INCREMENT, COMMIT, ROLLBACK, TRANSACTION, GRANT, REVOKE, TRUNCATE, SHOW, JOB, JOBS, LOG, LAST JOIN, INTO, OUTFILE, @@execute_mode='online', @@execute_mode='offline'"
# work
sql_keyword_string = "SELECT, FROM, WHERE, AND, OR, NOT, ORDER BY, GROUP BY, HAVING, COUNT, SUM, AVG, MAX, MIN, ON, AS, IN, BETWEEN, LIKE, LIMIT, UNION, UNION ALL, INSERT INTO, VALUES, UPDATE, SET, DELETE, CREATE DATABASE, DROP DATABASE, CREATE TABLE, DROP TABLE, ADD, DROP,  DEFAULT, NULL, NOT NULL, SHOW, JOB, JOBS, LOG, LAST JOIN, INTO, OUTFILE"
# sql_keywords = map(str.strip, sql_keyword_string.split(","))
# TODO: too much and not work
sql_keywords = ['SELECT', 'INSERT', 'LOAD', 'CREATE DATABASE', 'CREATE TABLE', 'FROM']
fruits_completer = WordCompleter(sql_keywords, ignore_case=True)

session = PromptSession(history=FileHistory('history.txt'), auto_suggest=AutoSuggestFromHistory())


def print_colorful_text(color, text, end='\n'):
    color_codes = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
    }
    color_sequence = f"\033[{color_codes[color]}m"
    reset_sequence = "\033[0m"
    print(f"{color_sequence}{text}{reset_sequence}", end=end)


def user_print(text, end='\n'):
    print_colorful_text("blue", "USER > " + text, end)


def gpt_print(text, end='\n'):
    print_colorful_text("green", "GPT > " + text, end)


def openmldb_print(text, end='\n'):
    print_colorful_text("yellow", "OpenMLDB > " + text, end)

history_message_queue = Queue(maxsize=10)

system_message = {"role": "system", "content": "You are a helpful assistant."}

def call_chatgpt(prompt):
    # Set up the API client
    openai.api_key = config.get("OpenAI", "api_key")
    model_engine = config.get("OpenAI", "model_engine")

    if history_message_queue.full():
        history_message_queue.get()

    history_message_queue.put({"role": "user", "content": prompt})

    request_messages = list(history_message_queue.queue)
    request_messages.insert(0, system_message)

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=request_messages,
        stream=True,
        max_tokens=int(config.get("OpenAI", "max_tokens"))
        # "temperature": 0
    )

    # Print the response
    # output_text = response['choices'][0]['message']['content']
    # return output_text

    # create variables to collect the stream of events

    completion_text = ''
    # iterate through the stream of events
    gpt_print("", end='')
    for event in response:

        if "delta" in event['choices'][0] and "content" in event['choices'][0]['delta']:
            event_text = event['choices'][0]['delta']['content']  # extract the text
            completion_text += event_text  # append the text

            if event_text == "\n\n":
                pass
            else:
                print(event_text, end="")

    # print the time delay and text received
    # print(f"Full text received: {completion_text}")

    if history_message_queue.full():
        history_message_queue.get()

    history_message_queue.put({"role": "assistant", "content": completion_text})

    print("")


style = Style.from_dict({
    '': '#ff00ff',
})


db_name = "db10"

connection = connect(zk=config.get("OpenMLDB", "zk_cluster"), zkPath=config.get("OpenMLDB", "zk_root_path"))
cursor = connection.cursor()

#cursor.execute(f"create database if not exists {db_name}")

def is_dql(sql: str) -> bool:
    sql_keyword = sql.split()[0].upper()
    if sql_keyword in ["SELECT", "SHOW"]:
        return True
    else:
        return False

def is_show_joblog(sql: str) -> bool:
    if sql.lower().startswith("show joblog"):
        return True
    else:
        return False

def run_openmldb_sql(sql):
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        schema = [description[0] for description in cursor.description]

        if is_dql(sql):
            openmldb_print("Success to execute query SQL.")
            if is_show_joblog(sql):
                print(rows[0][0])
            else:
                print(tabulate(rows, headers=schema, tablefmt='grid'))
        else:
            openmldb_print(f"Success to execute SQL. Rows affected: {cursor.rowcount}")

    except DatabaseError as e:
        openmldb_print("Fail to execute SQL and get error message: ")
        openmldb_print(e.message)


def close():
    cursor.close()
    connection.close()


while True:
    try:
        user_input = session.prompt('USER > ', completer=fruits_completer, style=style)
        if user_input.lower() == 'q':
            break
        # print(f'You entered: {user_input}')
        #call_chatgpt(user_input)
        run_openmldb_sql(user_input)
    except KeyboardInterrupt:
        break
