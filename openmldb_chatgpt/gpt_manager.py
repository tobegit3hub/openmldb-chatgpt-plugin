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


class GptManager:

    def __init__(self, api_key: str, model_engine: str, max_tokens: int):
        openai.api_key = api_key

        self.model_engine = model_engine
        self.max_tokens = max_tokens

        HISTORY_MESSAGE_SIZE = 6
        self.history_message_queue = deque(maxlen=HISTORY_MESSAGE_SIZE)

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

        self.system_message = {"role": "system", "content": system_role_prompt}

    def call_chatgpt(self, prompt: str, update_history_message: bool = True):

        self.history_message_queue.append({"role": "user", "content": prompt})

        request_messages = list(self.history_message_queue)
        request_messages.insert(0, self.system_message)

        response = openai.ChatCompletion.create(
            model=self.model_engine,
            messages=request_messages,
            stream=True,
            temperature=0.3,
            max_tokens=self.max_tokens
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
            self.history_message_queue.append({"role": "assistant", "content": completion_text})
        else:
            self.history_message_queue.pop()

        print("")
