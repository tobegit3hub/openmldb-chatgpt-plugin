FROM tobegit3hub/portable-openmldb

RUN pip install openmldb-chatgpt
RUN pip install notebook

ADD start_notebook.sh ./

CMD ["bash", "-c", "./start.sh && openmldb-chatgpt"]
