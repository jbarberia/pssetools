.PHONY: clean install build

PYTHON27="C:/Python27/python.exe"
PYTHON39="C:/Anaconda3/python.exe"
PYTHON314="C:/Python314/python.exe"


clean:
	rm */*.pyc
	
install:
	$(PYTHON27) -m pip install .
	$(PYTHON39) -m pip install .
	$(PYTHON314) -m pip install .

build:
	$(PYTHON27) -m build .
