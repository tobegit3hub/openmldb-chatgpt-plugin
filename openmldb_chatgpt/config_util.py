
import os
import configparser

class ConfigUtil:


    @staticmethod
    def get_config():

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
        return config



