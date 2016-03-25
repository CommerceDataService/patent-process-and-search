## Running Tika in Docker

Example usage, starting up Tika in Docker and sending it a PDF file from which to extract text:

    docker-machine start default
    eval $(docker-machine env)
    docker run -d -p 9998:9998 ministryofjustice/tika
    curl -X PUT --data-binary @sample/fd2015007907-02-29-2016-1.pdf http://192.168.99.100:9998/tika --header "Content-type: application/pdf" > sample/fd2015007907-02-29-2016-1.txt
