FROM python:3.12

WORKDIR /app

COPY ../requirements.txt /app/requirements.txt

COPY ../src /app/src

COPY ../pyproject.toml /app/pyproject.toml

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install -r /app/requirements.txt

RUN python3 -m nltk.downloader punkt

RUN python3 -m nltk.downloader punkt_tab

RUN python3 -m pip install .

EXPOSE 8000

CMD [ "fastapi", "run", "/app/src/vip_login/main.py", "--port", "8000" ]
