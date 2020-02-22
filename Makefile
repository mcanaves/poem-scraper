.DEFAULT_GOAL := help

.PHONY: help
help:  ## Shows this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target> <arg=value>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m  %s\033[0m\n\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 🚀 Getting started

.PHONY: build
build: ## Create a virtualenv and install dependencies
	./scripts/install

.PHONY: scraping
scraping: ## Start scraping poems. Arguments: options=[OPTIONS] will pass args to script. Use --help to see all available options.
	./venv/bin/python scraper.py $(options)

##@ 🛠  Testing and development

.PHONY: lint
lint: ## Check of fix code lint. Arguments: fix=yes will force changes
	./scripts/lint $(fix)

.PHONY: recreate
recreate: ## Make a new clean environment including dependencies
	rm -r ./venv
	make build
