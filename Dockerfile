#FROM apache/airflow:2.2.3
#USER root
#COPY requirements.txt /requirements.txt
#RUN pip install --user --upgrade pip
#RUN pip install --no-cache-dir --user -r /requirements.txt
#RUN apt-get update \
#  && apt-get install -y --no-install-recommends \
#         vim \
#  && apt-get autoremove -yqq --purge \
#  && apt-get clean \
#  && rm -rf /var/lib/apt/lists/*
#USER airflow
FROM apache/airflow:2.2.3
RUN python3 -m pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirements.txt
USER airflow
COPY --chown=airflow:root airflow_script.py /opt/airflow/dags
COPY --chown=airflow:root penguin_trainer.py /opt/airflow/dags





# docker run --rm -ti --platform linux/arm/v7 ubuntu:latest uname -m armv7l

# docker run --rm -ti --platform linux/amd64 ubuntu:latest uname -m x86_64





#docker run --rm -it --entrypoint bash patrik117/airflow-vanillia:2v37
#https://airflow.apache.org/docs/helm-chart/stable/quick-start.html
#https://docs.docker.com/docker-hub/
#https://airflow.apache.org/docs/apache-airflow/1.10.1/scheduler.html


#docker build -t patrik117/tfx:v1 .
#docker push patrik117/tfx:v1


#helm upgrade $RELEASE_NAME apache-airflow/airflow --namespace $NAMESPACE \
 #   --set images.airflow.repository=patrik117/airflow-vanillia \
  #  --set images.airflow.tag=2v12
   #  --timeout 10m30s


    #kubectl port-forward svc/$RELEASE_NAME-webserver 8080:8080 --namespace $NAMESPACE


