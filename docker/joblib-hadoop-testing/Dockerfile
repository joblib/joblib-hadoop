FROM joblib/joblib-hadoop-nodemanager:latest
MAINTAINER Alexandre Abadie <alexandre.abadie@gmail.com>

WORKDIR /work
RUN git clone https://github.com/joblib/joblib-hadoop.git

WORKDIR /work/joblib-hadoop
RUN pip install -r requirements.txt .

CMD ["bash"]
