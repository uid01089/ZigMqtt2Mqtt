pip freeze > requirements.txt
docker build -t zigmqtttomqtt -f Dockerfile .
docker tag zigmqtttomqtt:latest docker.diskstation/zigmqtttomqtt
docker push docker.diskstation/zigmqtttomqtt:latest