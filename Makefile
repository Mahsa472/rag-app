# Makefile for DVC reproduction in EC2
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
DVC := $(VENV)/bin/dvc

.PHONY: venv install repro status clean

# Create virtual environment # make venv
venv:
	python3.10 -m venv $(VENV)

# Install dependencies # make install
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install "dvc[s3]"

# Reproduce DVCt # make repro
repro:
	$(DVC) repro

# Show DVC status # make status
status:
	$(DVC) status

# Clean up virtual environment # make clean
clean:
	rm -rf $(VENV)
