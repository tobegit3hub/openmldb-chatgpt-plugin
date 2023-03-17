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

# Update the code and upload the package to pypi
# 1. python ./setup.py bdist_wheel --universal
# 2. twine upload dist/openmldb-chatgpt-x.x.x-py2.py3-none-any.whl

from setuptools import setup, find_packages

setup(
    name="openmldb-chatgpt",
    version="0.1.0",
    author="tobe",
    author_email="tobeg3oogle@gmail.com",
    url="https://github.com/tobegit3hub/openmldb-chatgpt-plugin",
    description="The ChatGPT plugin to enhance OpenMLDB.",
    packages=find_packages(),
    install_requires=[
        'configparser', 'prompt_toolkit', 'tabulate', 'openai', 'openmldb'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "openmldb-chatgpt=openmldb_chatgpt.cli:main"
        ],
    })
