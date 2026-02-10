.PHONY: run test clean lint

run:
	./venv/bin/uvicorn app.main:app --reload

test:
	./venv/bin/pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

lint:
	# Add linting commands if tools are installed (flake8, black, etc.)
	@echo "Linting not configured yet."
