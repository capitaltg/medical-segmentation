FROM python:3-slim
WORKDIR /app

RUN apt-get update
RUN apt-get install -y curl unzip

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip && rm awscliv2.zip
RUN ./aws/install
RUN rm -rf ./aws/

COPY credentials /app/credentials
ENV AWS_CONFIG_FILE=/app/credentials

RUN aws s3 cp s3://medical-image-segmentation/lungs/70-10-20-3D/train-output.zip .
RUN aws s3 cp s3://medical-image-segmentation/lungs/70-10-20-3D/val-output.zip .
RUN aws s3 cp s3://medical-image-segmentation/lungs/70-10-20-3D/test-output.zip .

RUN unzip '*-output.zip'
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY *.py .
COPY *.ipynb .

EXPOSE 8888

CMD ["python3", "-m", "jupyter", "notebook", "--ip", "0.0.0.0", "--allow-root"]
