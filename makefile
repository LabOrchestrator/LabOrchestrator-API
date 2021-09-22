VERSION := $(shell python3 setup.py --version)


install-dev:
	python3 -m pip install --upgrade build
	python3 -m pip install --upgrade twine

git-tag:
	git tag "v$(VERSION)"

git-release:
	git push
	git push --tags

docker-build:
	docker build -t biolachs2/lab_orchestrator:v$(VERSION) .
	docker build -t biolachs2/lab_orchestrator:latest .

docker-push:
	docker push biolachs2/lab_orchestrator:v$(VERSION)
	docker push biolachs2/lab_orchestrator:latest

release: test docker-build git-tag docker-push git-release

test:
	./manage.py test
