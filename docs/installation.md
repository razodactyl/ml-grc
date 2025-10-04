# Installation Guide

## Prerequisites

- Python 3.6 or higher
- pip package manager

## Installation Methods

### From Source

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ml-grc
   ```

2. Install in development mode:

   ```bash
   pip install -e .
   ```

3. Run the application:
   ```bash
   grc
   ```

### Using pip

```bash
pip install grc
```

## Troubleshooting

### Common Issues

1. **PyQt5 Installation Issues**: On some systems, you may need to install PyQt5 separately:

   ```bash
   pip install PyQt5
   ```

2. **OpenCV Issues**: If you encounter OpenCV problems, try:

   ```bash
   pip install opencv-python
   ```

3. **Permission Errors**: Use `pip install --user` for user-only installation.
