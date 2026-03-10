SHELL := /bin/bash
PYTHON ?= python3
PYTHONPATH := v2/src

.PHONY: help demo test adrs

help:
	@echo "Targets:"
	@echo "  make demo   - Run v2 local demo flow (no Spark/Kafka required)"
	@echo "  make test   - Run v2 pytest suite"
	@echo "  make adrs   - List v2 ADR files"

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) v2/scripts/demo_pipeline.py

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q v2/tests

adrs:
	@find v2/docs/adrs -maxdepth 1 -type f | sort
