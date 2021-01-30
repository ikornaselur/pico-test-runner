mypy:
	@poetry run mypy src/pico_test_runner/* tests/*

flake8:
	@poetry run flake8 src/pico_test_runner/* tests/*

lint: mypy flake8

test: unit_test

unit_test:
	@poetry run pytest tests/unit -xvvs

shell:
	@poetry run ipython

install_git_hooks:
	@ln -s /Users/axel/Projects/pico-test-runner/.hooks/pre-push .git/hooks/pre-push
