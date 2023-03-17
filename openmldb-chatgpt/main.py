#!/usr/bin/env python3

import openai

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from collections import deque
from openmldb.dbapi import connect
from openmldb.dbapi import DatabaseError
from tabulate import tabulate

from print_util import PrintUtil
from sql_util import SqlUtil
from config_util import ConfigUtil


config = ConfigUtil.get_config()

session = PromptSession(history=FileHistory('history.txt'), auto_suggest=AutoSuggestFromHistory())



last_sql = ""
last_sql_error_message = ""
HISTORY_MESSAGE_SIZE = 6
history_message_queue = deque(maxlen=HISTORY_MESSAGE_SIZE)

system_role_prompt = """
You are a helpful assistant and database expert. You are using OpenMLDB database and teach users how to use SQL.

OpenMLDB has 3 databases including "db1", "school", "fin tect". Database "db1" has 1 tables including "t1". Database "school" has 2 tables including "student", "teacher". Database "fin_tect" has 3 tables including "bank", "user", "trade".

SQL tables and their attributes:
# db1.t1 (col1)
# school.student (id, name, age)
# school.teacher (id, name, subject)
# fin_tect.bank (id, name, department_id)
# fin_tect.user (id, name, address）
# fin_tect.trade (id, employee_id, amount, date)
"""

system_message = {"role": "system", "content": system_role_prompt}




def call_chatgpt(prompt, update_history_message: bool = True):
    # Set up the API client
    openai.api_key = config.get("OpenAI", "api_key")
    model_engine = config.get("OpenAI", "model_engine")

    history_message_queue.append({"role": "user", "content": prompt})

    request_messages = list(history_message_queue)
    request_messages.insert(0, system_message)

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=request_messages,
        stream=True,
        temperature=0.3,
        max_tokens=int(config.get("OpenAI", "max_tokens"))
    )

    completion_text = ''
    # iterate through the stream of events
    PrintUtil.gpt_print("", end='')
    for event in response:

        if "delta" in event['choices'][0] and "content" in event['choices'][0]['delta']:
            event_text = event['choices'][0]['delta']['content']  # extract the text
            completion_text += event_text  # append the text

            if event_text == "\n\n":
                pass
            else:
                print(event_text, end="")

    if update_history_message:
        history_message_queue.append({"role": "assistant", "content": completion_text})
    else:
        history_message_queue.pop()

    print("")



connection = connect(zk=config.get("OpenMLDB", "zk_cluster"), zkPath=config.get("OpenMLDB", "zk_root_path"))
cursor = connection.cursor()




help_message = """
#######                      #     # #       ######  ######      #####                       #####  ######  #######
#     # #####  ###### #    # ##   ## #       #     # #     #    #     # #    #   ##   ##### #     # #     #    #
#     # #    # #      ##   # # # # # #       #     # #     #    #       #    #  #  #    #   #       #     #    #
#     # #    # #####  # #  # #  #  # #       #     # ######     #       ###### #    #   #   #  #### ######     #
#     # #####  #      #  # # #     # #       #     # #     #    #       #    # ######   #   #     # #          #
#     # #      #      #   ## #     # #       #     # #     #    #     # #    # #    #   #   #     # #          #
####### #      ###### #    # #     # ####### ######  ######      #####  #    # #    #   #    #####  #          #

OpenMLDB ChatGPT 插件是一个集成了强大的 GPT 模型的 OpenMLDB 增强工具. 你可以在命令行中使用到以下功能：

1. 直接执行 OpenMLDB SQL 语句，例如 "SELECT 100"、"SHOW JOBS" 等，可立即返回计算结果。
2. 如果 SQL 执行成功，会自动解析 SQL 语义，例如输入"解释上面的SQL含义"、"分析上面的表数据"。
3. 如果 SQL 执行失败，会自动分析失败原因，例如输入 "解释SQL失败原因"、"改正上面的SQL语句"。
4. 如果不了解SQL语法或想了解OpenMLDB可直接提问，例如输入 "创建名为db1的数据库"、"查询系统有多少张表"
5. 所有自然语言提问都会保留上下文，可直接提问"上一个SQL是什么含义"、"请帮我优化上一个SQL语句"。
6. 如果模型返回的结果补全（因token数量限制），输入 "继续" 或者 "continuous" 继续查看模型返回的结果。
7. 使用 "help" 命令可打印帮助文档，使用 "q" 或 "quit" 命令可退出命令行。
"""


def run_openmldb_sql(sql) -> bool:
    global last_sql
    global last_sql_error_message

    last_sql = sql

    try:
        cursor.execute(sql)

        if SqlUtil.is_dql(sql):
            PrintUtil.openmldb_print("Success to execute query SQL.")

            rows = cursor.fetchall()
            schema = [description[0] for description in cursor.description]

            if SqlUtil.is_show_joblog(sql):
                print(rows[0][0])
            else:
                # TODO: We may use GPT to analyse output data
                table_string = tabulate(rows, headers=schema, tablefmt='grid')
                print(table_string)

        else:
            PrintUtil.openmldb_print(f"Success to execute SQL. Rows affected: {cursor.rowcount}")

        return True
    except DatabaseError as e:
        PrintUtil.openmldb_print("Fail to execute SQL and get error message: ")
        PrintUtil.openmldb_print(e.message)
        last_sql_error_message = e.message
        return False


def close():
    cursor.close()
    connection.close()


def print_help_message():
    PrintUtil.print_colorful("blue", help_message)


def main():
    completer = WordCompleter(SqlUtil.autocomplete_keywords(), ignore_case=True)
    style = Style.from_dict({
        '': '#ff00ff',
    })

    print_help_message()
    while True:
        try:
            user_input = session.prompt('USER > ', completer=completer, style=style)

            if user_input.lower() == 'q' or user_input.lower() == 'q':
                close()
                break

            elif user_input.lower() == "help":
                print_help_message()

            else:
                if SqlUtil.is_possible_sql(user_input):
                    is_success = run_openmldb_sql(user_input)
                    if is_success:
                        # Use GPT to anaylse SQL, optimize SQL or anaylse data
                        gpt_prompt = f"分析成功执行的SQL语句'{user_input}'"
                        PrintUtil.gpt_print(gpt_prompt)
                        call_chatgpt(gpt_prompt, update_history_message=False)

                        gpt_prompt = f"执行完SQL语句'{user_input}'，然后建议执行什么操作"
                        PrintUtil.gpt_print(gpt_prompt)
                        call_chatgpt(gpt_prompt, update_history_message=False)
                    else:
                        # Use GPT to anaylse the error message and correct the SQL
                        gpt_prompt = f"分析SQL失败原因，SQL语句是'{user_input}'，错误信息是'{last_sql_error_message}'"
                        PrintUtil.gpt_print(gpt_prompt)
                        call_chatgpt(gpt_prompt, update_history_message=False)

                else:
                    call_chatgpt(user_input)

        except KeyboardInterrupt:
            close()
            break


if __name__ == "__main__":
    main()
