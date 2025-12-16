# PyPI Publication - Quick Start Guide

This repository is now fully configured and ready for PyPI publication! 🚀

## What Was Done

The following files have been added/modified to enable PyPI publishing:

### New Files Created
1. **pyproject.toml** - Modern package metadata (PEP 621 compliant)
2. **MANIFEST.in** - Controls which files are included in distributions
3. **PYPI_PUBLISHING.md** - Detailed step-by-step publishing instructions
4. **PACKAGING_SUMMARY.md** - Comprehensive documentation of all packaging decisions
5. **.github/workflows/publish-to-pypi.yml** - GitHub Actions workflow for automated publishing

### Modified Files
1. **setup.py** - Updated to minimal version with optional Java toolkit build

## Quick Start: Publishing to PyPI

### Prerequisites
```bash
pip install build twine
```

### Step 1: Build the Package
```bash
python -m build
```

This creates:
- `dist/catena4j-2.0.0.tar.gz` (source distribution)
- `dist/catena4j-2.0.0-py3-none-any.whl` (wheel distribution)

### Step 2: Test on TestPyPI (Recommended)
```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ catena4j
```

### Step 3: Publish to PyPI
```bash
twine upload dist/*
```

You'll be prompted for your PyPI username and password (or API token).

## Automated Publishing with GitHub Actions

The repository includes a GitHub Actions workflow that automatically publishes to PyPI when you create a release:

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a GitHub release with a tag (e.g., `v2.0.1`)
4. GitHub Actions automatically builds and publishes to PyPI

### Required Secrets
Add these to your GitHub repository settings:
- `PYPI_API_TOKEN` - Your PyPI API token
- `TEST_PYPI_API_TOKEN` - Your TestPyPI API token (optional)

## Package Information

- **Name**: catena4j
- **Version**: 2.0.0
- **License**: MIT
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12+
- **Dependencies**: None (pure Python stdlib)
- **Size**: ~922KB (wheel), ~498KB (source)

## Installation (After Publishing)

Once published to PyPI, users can install with:
```bash
pip install catena4j
```

Then use the CLI:
```bash
catena4j pids
catena4j checkout -p Chart -v 15b1 -w ./buggy
```

## Validation Results

✅ **All tests passed:**
- Package builds successfully
- Both sdist and wheel created
- All data files included (projects/, resources/, toolkit/)
- Package installs correctly
- Entry point works
- Metadata is valid
- Security scan: 0 alerts
- Code review: All feedback addressed

## Documentation

For detailed information, see:
- **PYPI_PUBLISHING.md** - Complete publishing guide with troubleshooting
- **PACKAGING_SUMMARY.md** - Detailed explanation of all packaging decisions
- **README.md** - Main project documentation

## Notes

### Java Toolkit Build
The package includes an optional Java toolkit that requires:
- Java JDK 8+
- Defects4J v2.0 (optional)

If these are not available during build, the toolkit is skipped with a warning. The package still builds and installs correctly.

### Twine Validation Warning
You may see a warning about `license-file` when running `twine check`. This is a false positive due to using Metadata-Version 2.4. The package will upload and install correctly - this warning can be safely ignored.

## Next Steps

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Create TestPyPI account**: https://test.pypi.org/account/register/ (for testing)
3. **Generate API tokens** for both services
4. **Test on TestPyPI** first to verify everything works
5. **Publish to PyPI** when ready

## Support

For questions or issues with packaging:
- Check **PYPI_PUBLISHING.md** for detailed instructions
- Check **PACKAGING_SUMMARY.md** for design decisions
- See [Python Packaging Guide](https://packaging.python.org/)
- Open an issue on GitHub

---

**The repository is ready for immediate PyPI publication!** 🎉
