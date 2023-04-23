CORE_IMAGE ?= arrticle-rec-core:latest
SUMMARIZER_IMAGE ?= arrticle-rec-summarizer:latest
SIMILARITY_SCORER_IMAGE ?= arrticle-rec-similarity-scorer:latest

build-core:
	@echo "Building core..."
	@cd core && docker build -t $(CORE_IMAGE) .

publish-core:
	@echo "Publishing core..."
	@docker push $(CORE_IMAGE)

build-and-publish-core: build-core publish-core

build-content-summarizer:
	@echo "Building content summarizer..."
	@cd modules/content_summarizer && docker build -t $(SUMMARIZER_IMAGE) .

build-similarity-scorer:
	@echo "Building content summarizer..."
	@cd modules/similarity_scorer && docker build -t $(SIMILARITY_SCORER_IMAGE) .