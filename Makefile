

clean:
	rm */*.pyc
	
install:
	python  -m pip install .
	python2 -m pip install .

build:
	python -m build
