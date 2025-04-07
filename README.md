## Exodus: Agentic Pentesting Suite

![image.png](./logo.png)

Exodus is an agentic pentesting suite that fuses LLMs with tools in Kali Linux to perform attacks on networks. Built for [Sundai](https://sundai.club) hackathon.

### Getting Started

- Make sure you have `docker` installed on your system.
- Make sure you have `uv` installed on your system (use `brew` or `pip`). 
- Run `./build.sh` to build a Docker image for Kali called `kali`.
- Start the Docker daemon by opening Docker desktop.
- Run `./start.sh` to start the `kali` Docker container.
- Run `uv pip install -r requirements.txt`
- Run `uv venv`
- Run `uv run main.py`
