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
import configparser
import getpass
import copy
import logging
logger = logging.getLogger(__name__)


class ConfigUtil:

    def __init__(self):
        self.config_file_path = os.path.join(os.path.expanduser("~"), ".openmldb/", "openmldb-chatgpt.ini")
        self.config = configparser.ConfigParser()
        self.init_config()
        self.print_config()

    @staticmethod
    def use_default_value(text: str) -> bool:
        if text == "" or text.lower() == "y" or text.lower() == "yes":
            return True
        else:
            return False

    @staticmethod
    def print_config_parser(config):
        # Print the contents of the ConfigParser object
        for section in config.sections():
            print(f"[{section}]")
            for option in config.options(section):
                value = config.get(section, option)
                print(f"{option} = {value}")

    def init_config(self):
        # Create directory if not exists
        config_directory = os.path.join(os.path.expanduser("~"), ".openmldb/")
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)
            logger.info(f"Create the directory of {config_directory}")

        self.config.read(self.config_file_path)

        if not self.config.has_section("OpenAI"):
            self.config.add_section("OpenAI")

        if not self.config.has_option("OpenAI", "api_key"):
            self.config.set("OpenAI", "api_key", getpass.getpass("Please input your OpenAI API Key (sk-xxx): "))

        if not self.config.has_option("OpenAI", "model_engine"):
            text = input("Please choose GPT model_engine (y/yes for default gpt-3.5-turbo): ")
            if ConfigUtil.use_default_value(text):
                self.config.set("OpenAI", "model_engine", "gpt-3.5-turbo")
            else:
                self.config.set("OpenAI", "model_engine", text)

        if not self.config.has_option("OpenAI", "max_tokens"):
            text = input("Please choose GPT max_tokens (y/yes for default 256): ")
            if ConfigUtil.use_default_value(text):
                self.config.set("OpenAI", "max_tokens", "256")
            else:
                self.config.set("OpenAI", "max_tokens", text)

        if not self.config.has_section("OpenMLDB"):
            self.config.add_section("OpenMLDB")

        if not self.config.has_option("OpenMLDB", "zk_cluster"):
            text = input("Please choose OpenMLDB zk_cluster (y/yes for default 0.0.0.0:2181): ")
            if ConfigUtil.use_default_value(text):
                self.config.set("OpenMLDB", "zk_cluster", "0.0.0.0:2181")
            else:
                self.config.set("OpenMLDB", "zk_cluster", text)

        if not self.config.has_option("OpenMLDB", "zk_root_path"):
            text = input("Please choose OpenMLDB zk_root_path (y/yes for default /openmldb): ")
            if ConfigUtil.use_default_value(text):
                self.config.set("OpenMLDB", "zk_root_path", "/openmldb")
            else:
                self.config.set("OpenMLDB", "zk_root_path", text)

        with open(self.config_file_path, "w") as config_file:
            self.config.write(config_file)

    def print_config(self):
        logger.info(f"Please check config in {self.config_file_path}")

        safe_config = copy.deepcopy(self.config)
        safe_config.set("OpenAI", "api_key", "[Hide the OpenAI API Key]")
        ConfigUtil.print_config_parser(safe_config)
