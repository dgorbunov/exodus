docker build -t kali .
docker run --cap-add=NET_ADMIN --name kali -d -it kali
