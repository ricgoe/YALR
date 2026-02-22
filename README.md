# YALR - Visual Lip Reading with AI
<p align="center">
  <img width=50% alt="pipeline" src="https://github.com/user-attachments/assets/727375ba-e043-40f2-9bbe-adb1ce9d64ef" />
</p>
YALR (Yet Another Lip Reader) is a computer vision–based lip reading system for sentence-level speech recognition from visual input only.
It combines MediaPipe-based mouth ROI extraction with a pretrained AV-HuBERT model and evaluates its applicability to real-world scenarios.
The project explores the practical challenges of visual-only speech recognition, including viseme ambiguity, non-labial sounds, and real-world recording conditions, and includes a web-based demonstrator with video transcription.

# Installation Guide

## Requirements

- Ubuntu (20.04 / 22.04 recommended)
- Python **3.10**
- Node.js **22**

---
# Clone required Repositories
```bash
git clone https://github.com/ricgoe/YALR.git
cd YALR
git submodule update --init
```
# Python Setup

## Install Python 3.10 (Ubuntu)

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-dev python3.10-venv python3.10-distutils build-essential ffmpeg
```
## Create Virtual Environment

```bash
python3.10 -m venv .venv
```

---

## Activate Virtual Environment

```bash
source .venv/bin/activate
```

---

## Downgrade pip

```bash
pip install pip==24
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Frontend Setup (Node.js 22 via nvm)

## Install nvm

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

Verify nvm installation after shell reload:

```bash
nvm --version
```

---

## Install Node.js 22

```bash
nvm install 22
nvm use 22
cd ./frontend && npm install
```

Verify installation:

```bash
node -v
npm -v
```

---


## Usage
<p align="center">
  <img width=50% alt="web_based" src="https://github.com/user-attachments/assets/9066af3e-33ac-4a2c-93a8-ab10bb66ce90" />
</p>


> [!IMPORTANT]  
> It is necessary to use two terminal instances (one for frontend, one for backend)

### Inside Backend Terminal
```bash
cd YALR
uvicorn api:app --host 0.0.0.0
```
### Inside Frontend Terminal
```bash
cd YALR/frontend
npm run dev
```

