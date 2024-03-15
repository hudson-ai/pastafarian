PKG = pastafarian

build:
	pip install build
	python -m build

install: build
	pip install dist/*.tar.gz

develop:
	pip install -e .

check:
	pytest -v tests

uninstall:
	pip uninstall $(PKG)

clean:
	rm -rvf dist/ build/ src/*.egg-info
