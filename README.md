# YALR - Visuelles Lippenlesen mit KI
<img width="800" height="400" alt="pipeline" src="https://github.com/user-attachments/assets/727375ba-e043-40f2-9bbe-adb1ce9d64ef" />

# Installation Guide

## Requirements

- Ubuntu (20.04 / 22.04 recommended)
- Python **3.10**
- Node.js **22**
- build-essential

---

# Python Setup

## Install Python 3.10 (Ubuntu)

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-dev python3.10-venv python3.10-distutils build-essential
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

## Up-/ Downgrade pip

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
```

Verify installation:

```bash
node -v
npm -v
```

---


## Usage
<img width="800" height="500" alt="web_based" src="https://github.com/user-attachments/assets/9066af3e-33ac-4a2c-93a8-ab10bb66ce90" />
