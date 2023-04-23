CORE_IMAGE ?= arrticle-rec-core:latest

build-core:
	@echo "Building core..."
	@cd core && docker build -t $(CORE_IMAGE) .

publish-core:
	@echo "Publishing core..."
	@docker push $(CORE_IMAGE)

build-and-publish-core: build-core publish-core