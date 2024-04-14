poetry-install:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install

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
