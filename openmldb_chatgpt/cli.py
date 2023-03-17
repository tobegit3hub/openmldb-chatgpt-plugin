#!/usr/bin/env python3

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

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from print_util import PrintUtil
from sql_util import SqlUtil
from config_util import ConfigUtil
from openmldb_manager import OpenmldbManager
from gpt_manager import GptManager
from help_util import HelpUtil


def main():
    session = PromptSession(history=FileHistory('history.txt'), auto_suggest=AutoSuggestFromHistory())
    completer = WordCompleter(SqlUtil.autocomplete_keywords(), ignore_case=True)
    style = Style.from_dict({
        '': '#ff00ff',
    })

    config = ConfigUtil.get_config()
    gpt_manager = GptManager(config.get("OpenAI", "api_key"), config.get("OpenAI", "model_engine"), int(config.get("OpenAI", "max_tokens")))
    openmldb_manager = OpenmldbManager(config.get("OpenMLDB", "zk_cluster"), config.get("OpenMLDB", "zk_root_path"))
    HelpUtil.print_help_message()
    while True:
        try:
            user_input = session.prompt('USER > ', completer=completer, style=style)

            if user_input.lower() == 'q' or user_input.lower() == 'q':
                break

            elif user_input.lower() == "help":
                HelpUtil.print_help_message()

            else:
                if SqlUtil.is_possible_sql(user_input):
                    is_success = openmldb_manager.run_openmldb_sql(user_input)
                    if is_success:
                        # Use GPT to anaylse SQL, optimize SQL or anaylse data
                        gpt_prompt = f"分析成功执行的SQL语句'{user_input}'"
                        PrintUtil.gpt_print(gpt_prompt)
                        gpt_manager.call_chatgpt(gpt_prompt, update_history_message=False)

                        gpt_prompt = f"执行完SQL语句'{user_input}'，然后建议执行什么操作"
                        PrintUtil.gpt_print(gpt_prompt)
                        gpt_manager.call_chatgpt(gpt_prompt, update_history_message=False)
                    else:
                        # Use GPT to anaylse the error message and correct the SQL
                        gpt_prompt = f"分析SQL失败原因，SQL语句是'{user_input}'，错误信息是'{openmldb_manager.last_sql_error_message}'"
                        PrintUtil.gpt_print(gpt_prompt)
                        gpt_manager.call_chatgpt(gpt_prompt, update_history_message=False)

                else:
                    gpt_manager.call_chatgpt(user_input)

        except KeyboardInterrupt:
            break

    openmldb_manager.close()


if __name__ == "__main__":
    main()
