# Makefile
.PHONY: ci

ci:
	@echo "🔄 Installing dev dependencies..."
	@pip install --upgrade pip
	@pip install -q -e '.[dev]'
	@echo "🔍 Running ruff check..."
	@ruff check .
	@echo "🔍 Running mypy type check..."
	@mypy src/
	@echo "🧪 Running tests..."
	@pytest -q
	@echo "✅ All checks passed!" 