# Contributing to Twenty MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Twenty MCP Server project.

## Code of Conduct

Be respectful, constructive, and inclusive. Treat others with kindness and professionalism.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Environment details (OS, Python version, Twenty CRM version)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Include:

- A clear and concise description of the enhancement
- Use cases and benefits
- Possible implementation approaches (if applicable)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards
3. **Add tests** for new features or bug fixes
4. **Update documentation** as needed
5. **Run tests** and linting to ensure everything passes
6. **Commit** with a clear commit message
7. **Push** to your fork and submit a pull request

### Coding Standards

- Use Python 3.10+ type hints
- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Keep functions focused and modular
- Write meaningful commit messages
- Use descriptive variable and function names

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=twenty_mcp_server tests/
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type checking
mypy src/
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/BrusCode/twenty-mcp-server.git
cd twenty-mcp-server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings
```

## Project Structure

```
twenty-mcp-server/
├── src/twenty_mcp_server/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── client.py          # Twenty API client
│   ├── server.py          # MCP server main
│   └── tools/
│       ├── people.py       # People operations
│       ├── companies.py    # Companies operations
│       ├── opportunities.py # Opportunities operations
│       ├── notes.py       # Notes operations
│       ├── tasks.py       # Tasks operations
│       └── metadata.py    # Metadata operations
├── tests/
│   └── test_server.py    # Unit and integration tests
└── docs/                # Documentation (if needed)
```

## Adding New Features

When adding new object types or features:

1. Create a new file in `src/twenty_mcp_server/tools/`
2. Define tools using the `@mcp.tool()` decorator
3. Define resources using the `@mcp.resource()` decorator
4. Import and register in `server.py`
5. Add tests to `tests/test_server.py`
6. Update README.md with documentation

## Integration Tests

Integration tests require real API credentials. They are skipped by default:

```bash
# Run integration tests
TWENTY_API_KEY=your_key TWENTY_BASE_URL=your_url pytest tests/ -v
```

## Questions?

Feel free to open an issue for questions or discussion!
