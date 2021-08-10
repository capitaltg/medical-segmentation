FROM python:3-slim
WORKDIR /app

RUN apt-get update
RUN apt-get install -y curl unzip
RUN apt-get install -y cmake

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip && rm awscliv2.zip
RUN ./aws/install
RUN rm -rf ./aws/

COPY requirements.txt ./
RUN python -m pip install scikit-build
RUN pip install -r requirements.txt

COPY *.py .

COPY *.ipynb .

EXPOSE 8888

CMD ["python3", "-m", "jupyter", "notebook", "--ip", "0.0.0.0", "--allow-root"]
