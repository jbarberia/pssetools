.PHONY: clean install build test

PYTHON27="C:/Python27/python.exe"
PYTHON314="C:/Python314/python.exe"


clean:
	rm */*.pyc
	
install:
	$(PYTHON27) -m pip install .
	$(PYTHON314) -m pip install -e .

build:
	$(PYTHON27) -m build .

test:
	$(PYTHON314) -m pytest
