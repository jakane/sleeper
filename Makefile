# Makefile for sleeper

VENV ?= .venv
PYTHON ?= python3
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV)/bin/pip

.DEFAULT_GOAL := help

.PHONY: help venv install dev test build clean distclean install-user

help:
	@echo "sleeper - Development & Automation Commands"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  help          Show this help message"
	@echo "  venv          Create virtual environment (.venv)"
	@echo "  install       Install package in editable mode into .venv"
	@echo "  dev           Set up .venv with development and build tools"
	@echo "  test          Run unit test suite using virtual environment"
	@echo "  build         Clean and build sdist and wheel packages"
	@echo "  clean         Remove build artifacts and Python bytecode caches"
	@echo "  distclean     Run clean and remove .venv directory"
	@echo "  install-user  Copy sleeper executable to ~/.local/bin"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

venv: $(VENV)/bin/activate

install: $(VENV)/bin/activate
	$(VENV_PIP) install --no-build-isolation -e .

dev: install
	$(VENV_PIP) install build setuptools

test: $(VENV)/bin/activate
	$(VENV_PYTHON) -m unittest discover -v -s tests

build: clean dev
	$(VENV_PYTHON) -m build --no-isolation

clean:
	rm -rf dist build src/*.egg-info *.egg-info .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete

distclean: clean
	rm -rf $(VENV)

install-user: install
	mkdir -p $(HOME)/.local/bin
	cp -f $(VENV)/bin/sleeper $(HOME)/.local/bin/sleeper
	chmod +x $(HOME)/.local/bin/sleeper
	@echo "Copied sleeper executable to $(HOME)/.local/bin/sleeper"
