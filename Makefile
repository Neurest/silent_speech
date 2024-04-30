poetry-install:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install
	poetry run pip install tts

check-quality:
	flake8 iclx
	mypy iclx

docker-build:
	docker build --platform linux/amd64 -t  nemodleosnu/neurest-silent_speech:0.1.0 -f Dockerfile .

docker-push:
	docker push nemodleosnu/neurest-silent_speech:0.1.0

docker-build-and-push: 
	$(MAKE) docker-build 
	$(MAKE) docker-push

record-reading:
	poetry run python data_collection/record_reading.py --output_directory data/tmp/record_reading --book_file data/tmp/book_file.txt --debug True

nltk-download-punkt:
	poetry run python -c "import nltk; nltk.download('punkt')"