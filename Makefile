
.PHONY: build check eval sync

build:
	python compile_prompt.py PromptSpec.yaml PromptPatches_example.yaml Runtime_Prompt.md

check:
	python sync_orchestrator.py --check || (echo 'Sync check failed' && exit 1)

eval:
	python eval_harness.py

sync: build check eval
	@echo 'Sync OK'
