.PHONY: install test clean

PYTHON27="C:/Python27/python.exe"
PYTHON314="C:/Python314/python.exe"

	
install:
	$(PYTHON27) -m pip install .	
	$(PYTHON314) -m pip install -e .

test:
	$(PYTHON314) -m pytest

clean:
	rm */*.pyc
