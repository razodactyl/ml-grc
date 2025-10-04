# Development Guide

## Project Structure

```
src/grc/
├── core/           # Core application logic
├── widgets/        # UI components
├── utils/          # Utility functions
└── config/         # Configuration
```

## Running Tests

```bash
python -m pytest tests/
```

## Code Style

This project follows PEP 8 guidelines. Use `black` for code formatting:

```bash
pip install black
black src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
