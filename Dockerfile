# Use the official Kali Linux image as the base image
FROM kalilinux/kali-rolling

# Update and install necessary packages and tools
RUN apt update && apt upgrade -y && apt install -y \
    kali-linux-default \
    && apt clean

# Expose any necessary ports
EXPOSE 8080

# Define default entrypoint or command to run your software
ENTRYPOINT ["bash"]
