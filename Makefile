AWS_REGION ?= us-east-1a # its for pushing image to ecr
ECR_ENDPOINT ?= ""
IMAGE_NAME ?= "pivot-peak"
TS=$(shell date +'%Y%m%d%H%M%S')
TAG=${IMAGE_NAME}:v${TS}

deploy: ## Rebuild docker image with a new tag and push to ECR
	docker build --build-arg AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} --build-arg AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} --build-arg AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} -t ${TAG} .
	aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_ENDPOINT}
	docker tag ${TAG} ${ECR_ENDPOINT}/${TAG}
	docker push ${ECR_ENDPOINT}/${TAG}
	$(shell sed -i 's/\(^ *image: *\).*/\1${ECR_ENDPOINT}\/${TAG}/' docker-compose.yaml)
	git add docker-compose.yaml
	git commit -m "autocommit: image version updated"
	eb deploy
.PHONY: rebuild


help: ## Show this help
	@echo ${TAG}
	@echo "\nSpecify a command. The choices are:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""

.PHONY: help