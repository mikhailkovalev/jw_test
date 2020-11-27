FROM python:3.6-slim
RUN mkdir /jw_test \
  && mkdir /jw_test/hosting \
  && mkdir /jw_test/jw_test \
  && mkdir /jw_test/management \
  && mkdir /jw_test/commands \
  && mkdir /jw_test/migrations
COPY manage.py \
    project_conf.yaml \
    project_test_conf.yaml \
    requirements.txt \
    # destination folder
    /jw_test/
COPY hosting/* /jw_test/hosting/
COPY hosting/migrations* /jw_test/hosting/migrations/
COPY hosting/management/* /jw_test/hosting/management/
COPY hosting/management/commands/* /jw_test/hosting/management/commands/
COPY jw_test/* /jw_test/jw_test/
RUN pip install -r /jw_test/requirements.txt
WORKDIR /jw_test/
