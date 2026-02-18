# YALR

Needed python3.10

on ubuntu:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-dev python3.10-venv python3.10-distutils build-essential

python3.11 -m venv ./.venv

source ./.venv/bin/activate && pip install pip==24
pip install -r requirements.txt