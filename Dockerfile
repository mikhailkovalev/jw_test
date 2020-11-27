FROM python:3.6-slim
RUN mkdir /jw_test
COPY ./ /jw_test/
RUN find /jw_test
RUN pip install -r /jw_test/requirements.txt
WORKDIR /jw_test/
