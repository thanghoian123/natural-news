python3 -m pip install --upgrade pip

python3 -m pip install -r requirements.txt

python3 -m pip install .

python3 -m nltk.downloader punkt

python3 -m nltk.downloader punkt_tab

python3 -m fastapi dev ./src/vip_login/main.py --port 8000
