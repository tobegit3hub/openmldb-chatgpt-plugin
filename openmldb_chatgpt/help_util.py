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

from print_util import PrintUtil


class HelpUtil:

    @staticmethod
    def print_help_message():

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
7. 使用 "help" 命令可打印帮助文档，使用 "q"、"quit"、"exit" 命令可退出命令行。
"""

        PrintUtil.print_colorful("cyan", help_message)
