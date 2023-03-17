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

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    # Load config from config file
    config = ConfigUtil().config

    # Init cli parameters
    history_file_path = os.path.join(os.path.expanduser("~"), ".openmldb/", "history.txt")
    cli_session = PromptSession(history=FileHistory(history_file_path), auto_suggest=AutoSuggestFromHistory())
    cli_completer = WordCompleter(SqlUtil.autocomplete_keywords(), ignore_case=True)
    cli_style = Style.from_dict({
        '': '#ff00ff',
    })


    # Connect with OpenMLDB
    openmldb_manager = OpenmldbManager(config.get("OpenMLDB", "zk_cluster"), config.get("OpenMLDB", "zk_root_path"))

    # Connect with OpenAI API key
    gpt_manager = GptManager(config.get("OpenAI", "api_key"), config.get("OpenAI", "model_engine"), int(config.get("OpenAI", "max_tokens")), openmldb_manager)

    # Print help message
    HelpUtil.print_help_message()

    while True:
        try:
            # Get user command
            user_input = cli_session.prompt('USER > ', completer=cli_completer, style=cli_style)

            # Quit command
            if user_input.lower() == 'q' or user_input.lower() == 'quit' or user_input.lower() == 'exit':
                break

            # Help command
            elif user_input.lower() == "help":
                HelpUtil.print_help_message()

            else:
                # Run SQL
                if SqlUtil.is_possible_sql(user_input):
                    # Run OpenMLDB SQL
                    is_success = openmldb_manager.run_openmldb_sql(user_input)

                    if is_success:
                        # Use GPT to anaylse SQL
                        gpt_prompt = f"分析成功执行的SQL语句'{user_input}'"
                        PrintUtil.gpt_print(gpt_prompt)
                        gpt_manager.run_gpt(gpt_prompt, update_history_message=False)

                        # Use GPT to suggest next step
                        gpt_prompt = f"执行完SQL语句'{user_input}'，然后建议执行什么操作"
                        PrintUtil.gpt_print(gpt_prompt)
                        gpt_manager.run_gpt(gpt_prompt, update_history_message=False)
                    else:
                        # Use GPT to anaylse the error message
                        gpt_prompt = f"分析SQL失败原因，SQL语句是'{user_input}'，错误信息是'{openmldb_manager.last_sql_error_message}'"
                        PrintUtil.gpt_print(gpt_prompt)
                        gpt_manager.run_gpt(gpt_prompt, update_history_message=False)

                # Chat with GPT
                else:
                    gpt_manager.run_gpt(user_input)

        except KeyboardInterrupt:
            break

    # Close OpenMLDB connection
    openmldb_manager.close()


if __name__ == "__main__":
    main()
