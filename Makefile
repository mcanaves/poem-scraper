.DEFAULT_GOAL := help

.PHONY: help
help:  ## Shows this help message.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target> <arg=value>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m  %s\033[0m\n\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 🚀 Getting started

.PHONY: build
build: ## Build docker image including base dependencies.
	docker-compose build

.PHONY: scraping
scraping: ## Start scraping. Arguments: options=[OPTIONS]. Use --help to see all options.
	docker-compose run --rm poems-scraper $(options)


##@ 🛠  Testing and development

.PHONY: lint
lint: ## Check of fix code lint. Arguments: fix=yes will force changes.
	docker-compose run --entrypoint sh --no-deps --rm poems-scraper /opt/scripts/lint.sh $(fix)
