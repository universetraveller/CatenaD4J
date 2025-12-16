# PyPI Publishing Guide for CatenaD4J

This document provides instructions for building and publishing the CatenaD4J package to PyPI.

## Prerequisites

### Required Tools
- Python 3.8 or higher
- `pip` package manager
- Java Development Kit (JDK) 8 or higher (for building the Java toolkit)
- `javac` and `jar` commands available in PATH

### Optional Dependencies
- Defects4J v2.0 (if you want full functionality)

### Install Build Tools

```bash
# Install build and publishing tools
pip install build twine
```

## Building the Package

### 1. Clean Previous Builds

Before building, remove any previous build artifacts:

```bash
# Remove build artifacts
rm -rf build/ dist/ *.egg-info

# Clean toolkit target (optional)
rm -rf toolkit/target/
```

### 2. Build the Distribution

The build process will:
1. Compile the Java toolkit (if Java source files are present)
2. Create the toolkit JAR file
3. Package Python code and data files
4. Create both wheel and source distributions

```bash
# Build the package
python -m build
```

This creates two files in the `dist/` directory:
- `catena4j-2.0.0-py3-none-any.whl` (wheel distribution - preferred)
- `catena4j-2.0.0.tar.gz` (source distribution)

### 3. Validate the Package

Before uploading, validate the package with `twine`:

```bash
# Check the distributions
twine check dist/*
```

This will verify:
- README renders correctly on PyPI
- Metadata is valid
- Package structure is correct

### 4. Test the Package Locally

Install the package locally to test it:

```bash
# Install in a virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the wheel
pip install dist/catena4j-2.0.0-py3-none-any.whl

# Test the installation
catena4j pids
catena4j --help

# Deactivate when done
deactivate
```

## Publishing to PyPI

### Test PyPI (Recommended First Step)

Test PyPI is a separate instance of PyPI for testing package uploads.

1. **Create a TestPyPI account**: https://test.pypi.org/account/register/

2. **Upload to TestPyPI**:

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*
```

You'll be prompted for your TestPyPI username and password.

3. **Test installation from TestPyPI**:

```bash
# Create a fresh virtual environment
python -m venv test_pypi_env
source test_pypi_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ catena4j

# Test the package
catena4j pids

# Deactivate
deactivate
```

### Production PyPI

Once you've verified the package on TestPyPI:

1. **Create a PyPI account**: https://pypi.org/account/register/

2. **Upload to PyPI**:

```bash
# Upload to PyPI
twine upload dist/*
```

3. **Verify on PyPI**: Visit https://pypi.org/project/catena4j/

4. **Install from PyPI**:

```bash
pip install catena4j
```

## Using API Tokens (Recommended)

For better security, use API tokens instead of username/password:

### For TestPyPI
1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token
3. Create/update `~/.pypirc`:

```ini
[testpypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmc...  # Your TestPyPI token
```

### For PyPI
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Update `~/.pypirc`:

```ini
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmc...  # Your PyPI token
```

Then upload without prompts:

```bash
twine upload --repository testpypi dist/*  # For TestPyPI
twine upload dist/*                         # For PyPI
```

## Versioning

The version is specified in `pyproject.toml`. To release a new version:

1. Update the version in `pyproject.toml`:
   ```toml
   version = "2.0.1"  # or whatever the next version is
   ```

2. Create a git tag:
   ```bash
   git tag -a v2.0.1 -m "Release version 2.0.1"
   git push origin v2.0.1
   ```

3. Build and upload the new version following the steps above

## Automated Publishing with GitHub Actions

For automated publishing on release, see `.github/workflows/publish-to-pypi.yml`.

## Package Contents

The package includes:

### Python Code
- `catena4j/` - Main Python package with CLI and core functionality

### Data Files
- `projects/` - Bug dataset (CSV files, patches, properties)
- `resources/` - Additional resources
- `toolkit/target/toolkit.jar` - Compiled Java toolkit (built during package build)

### Documentation
- `README.md` - Main documentation
- `LICENSE` - MIT License

## Troubleshooting

### Java Toolkit Build Fails

If the Java toolkit fails to build:
- Ensure `javac` and `jar` are in your PATH
- Check that JDK 8+ is installed: `javac -version`
- The build will warn but continue if toolkit compilation fails

### Defects4J Not Found

The package can be built without Defects4J installed. If Defects4J is available:
- The toolkit will be built with Defects4J dependencies
- If not available, the build continues with a warning

### Upload Fails

Common issues:
- **Version already exists**: You cannot re-upload the same version. Increment the version number.
- **Invalid credentials**: Check your username/password or API token
- **README rendering**: Run `twine check dist/*` to identify markup issues

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [TestPyPI](https://test.pypi.org/)
- [PEP 517 - Build Backend Interface](https://peps.python.org/pep-0517/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
