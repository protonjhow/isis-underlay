# POC Makefile

.DEFAULT_GOAL := help

.PHONY: help deploy destroy run-tests

spines := spine1,spine2
leaves := leaf1,leaf2,leaf3,leaf4

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

deploy: ## Deploy full topology
	sudo clab deploy --topo isis-underlay.yml --reconfigure 
	cp clab-isis-underlay/ansible-inventory.yml .
	#./config_servers.sh && sleep 5 # Give system some time to settle
	poetry run python3 scripts/push_fabric_configs.py

destroy: ## Destroy full topology
	sudo clab destroy --topo isis-underlay.yml --cleanup
	rm ansible-inventory.yml

redeploy: ## redeploy full topology
	sudo clab destroy --topo isis-underlay.yml --cleanup
	rm ansible-inventory.yml
	sudo clab deploy --topo isis-underlay.yml --reconfigure 
	cp clab-isis-underlay/ansible-inventory.yml .
	#./config_servers.sh && sleep 5 # Give system some time to settle
	poetry run python3 scripts/push_fabric_configs.py

run-tests: ## Run test
	python3 tests/test_fabric_interfaces.py
	python3 tests/test_fabric_underlay.py
	python3 tests/test_fabric_overlay.py
