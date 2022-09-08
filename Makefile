IMG ?= biancapetrut/simple_object_storage:dev

.PHONY: build
build: 
	python3 -m pip install wheel
	python3 setup.py bdist_wheel

.PHONY: docker_build
docker_build: build
	docker build . -t ${IMG}

.PHONY: docker_push
docker_push: docker_build
	docker push ${IMG}
