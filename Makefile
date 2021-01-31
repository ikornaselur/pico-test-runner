mypy:
	@poetry run mypy src/pico_test_runner/*

flake8:
	@poetry run flake8 src/pico_test_runner/*

lint: mypy flake8

shell:
	@poetry run ipython

install_git_hooks:
	@ln -s /Users/axel/Projects/pico-test-runner/.hooks/pre-push .git/hooks/pre-push
