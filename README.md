# mini-rag

this is a implementation of the rag model for question answering.
## requirements
python 3.8 or later

### install python using MiniConda
1) download and install MiniConda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install/overview)

2) create env using the following command
```bash
$ conda create -n mini-rag
```
3) Activate the environment:
```bash
$ conda activate mini-rag
```
### (optional) setup your command line for better readability
```bash
$ export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```
## installation
### install required packages
```bash
$ pip install -r requirements.txt
```
### setup the environment variables
```bash
$ cp .env.example .env
```
set your env variables in the `.env` file , like `OPENAI_API_KEY` value.
## run docker compose services
```bash
$ cd docker
$ cp .env.example .env
```
- update `.env` with your credentials

### run the fastapi server
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```