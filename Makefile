IMG ?= biancapetrut/simple_object_storage:dev
HELM_VERSION ?= 0.1.0

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

.PHONY: helm_package
helm_package: 
	mkdir -p dist
	HELM_EXPERIMENTAL_OCI=1 \
        helm package helm \
        --version ${HELM_VERSION} \
        -d dist/