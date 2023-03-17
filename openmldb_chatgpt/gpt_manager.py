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

import openai
from collections import deque

from print_util import PrintUtil
from openmldb_manager import OpenmldbManager

import logging
logger = logging.getLogger(__name__)


class GptManager:

    def __init__(self, api_key: str, model_engine: str, max_tokens: int, openmldb_manager: OpenmldbManager):
        # Set the OpenAI API key
        openai.api_key = api_key

        self.model_engine = model_engine
        self.max_tokens = max_tokens

        # Keep the history messages
        HISTORY_MESSAGE_SIZE = 6
        self.history_message_queue = deque(maxlen=HISTORY_MESSAGE_SIZE)

        # Generate the system role prompt
        system_role_prompt = GptManager.construct_system_role_prompt(openmldb_manager)
        logger.info(f"Use system role promet: {system_role_prompt}")
        self.system_message = {"role": "system", "content": system_role_prompt}

    @staticmethod
    def construct_system_role_prompt(openmldb_manager: OpenmldbManager) -> str:
        # The example system role prompt
        """
        You are a helpful assistant and database expert. You are using OpenMLDB database and teach users how to use SQL.

        OpenMLDB has 3 databases including "db1", "school", "fin tect".

        SQL tables and their attributes:
        # db1.t1 (col1)
        # school.student (id, name, age)
        # school.teacher (id, name, subject)
        # fin_tect.bank (id, name, department_id)
        # fin_tect.user (id, name, address）
        # fin_tect.trade (id, employee_id, amount, date)
        """

        db_names = openmldb_manager.get_database_names()
        db_num = len(db_names)
        db_names_string = ",".join(db_names)
        table_attributes = openmldb_manager.get_all_table_info(db_names)

        if db_num > 0:
            system_role_prompt = f"""You are a helpful assistant and database expert. You are using OpenMLDB database and teach users how to use SQL.
    
    OpenMLDB has {db_num} databases including {db_names_string}. 
    
    SQL tables and their attributes:
    {table_attributes}"""
        else:
            system_role_prompt = f"You are a helpful assistant and database expert. You are using OpenMLDB database and teach users how to use SQL."

        return system_role_prompt

    def run_gpt(self, prompt: str, update_history_message: bool = True):
        """
        Run GPT model with prompt.

        :param prompt The string to request GPT model.
        :update_history_message We should add the request and response message in history messages or not
        """

        # 1. Add the user prompt in messages
        self.history_message_queue.append({"role": "user", "content": prompt})

        # 2. Copy the history messages and add the system role prompt in the head of list
        request_messages = list(self.history_message_queue)
        request_messages.insert(0, self.system_message)

        # 3. Request OpenAI API and get streaming result
        response = openai.ChatCompletion.create(
            model=self.model_engine,
            messages=request_messages,
            stream=True,
            temperature=0.3,
            max_tokens=self.max_tokens
        )

        # Print the message in cli
        PrintUtil.gpt_print("", end='')

        # Iterate through the stream of events
        completion_text = ''
        for event in response:
            # Ignore the message which has no data
            if "delta" in event['choices'][0] and "content" in event['choices'][0]['delta']:
                event_text = event['choices'][0]['delta']['content']
                completion_text += event_text
                # Ignore the first message which is line breaker
                if event_text == "\n\n":
                    pass
                else:
                    # Append the message and print in the same line
                    print(event_text, end="")

        if update_history_message:
            # Append the response in history messages
            self.history_message_queue.append({"role": "assistant", "content": completion_text})
        else:
            # Pop the user's request in history messages
            self.history_message_queue.pop()

        # Print the line breaker in cli
        print("")
