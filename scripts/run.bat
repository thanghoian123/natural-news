python -m pip install --upgrade pip

python -m pip install -r ..\\requirements.txt

python -m pip install ..

python -m nltk.downloader punkt

python -m nltk.downloader punkt_tab

python -m fastapi dev ..\\src\\vip_login\\main.py --port 8000
