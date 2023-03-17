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

class PrintUtil:

    @staticmethod
    def print_colorful(color, text, end='\n'):
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

    @staticmethod
    def user_print(text, end='\n'):
        PrintUtil.print_colorful("blue", "USER > " + text, end)

    @staticmethod
    def gpt_print(text, end='\n'):
        PrintUtil.print_colorful("green", "GPT > " + text, end)

    @staticmethod
    def openmldb_print(text, end='\n'):
        PrintUtil.print_colorful("yellow", "OpenMLDB > " + text, end)
