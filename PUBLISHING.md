# Publishing Guide

This document explains how to publish new versions of the Ultimate Gemini MCP package to PyPI.

## Automated Publishing Workflow

The package uses GitHub Actions to automatically version and publish to PyPI when you push to the `main` branch.

## How It Works

### Version Bumping

The version is automatically incremented based on your commit message:

| Commit Message | Version Change | Example |
|----------------|----------------|---------|
| `Fix bug in image service` | Patch: `1.0.0` → `1.0.1` | Bug fixes, minor changes |
| `[minor] Add new aspect ratios` | Minor: `1.0.0` → `1.1.0` | New features |
| `[major] Breaking API changes` | Major: `1.0.0` → `2.0.0` | Breaking changes |

### Publishing Process

When you push to `main`:

1. ✅ **Version Detection**: Reads commit message to determine bump type
2. ✅ **Version Update**: Updates `pyproject.toml` and `src/__init__.py`
3. ✅ **Commit & Tag**: Commits changes and creates git tag (e.g., `v1.0.1`)
4. ✅ **Build**: Builds Python wheel and source distribution
5. ✅ **Publish**: Uploads to PyPI using `PYPI_API_TOKEN`
6. ✅ **Release**: Creates GitHub release with changelog

## Usage Examples

### Example 1: Bug Fix (Patch Version)

```bash
# Make your changes
git add .
git commit -m "Fix image saving error when directory doesn't exist"
git push origin main

# Result: 1.0.0 → 1.0.1
```

### Example 2: New Feature (Minor Version)

```bash
# Make your changes
git add .
git commit -m "[minor] Add support for WebP image format"
git push origin main

# Result: 1.0.0 → 1.1.0
```

### Example 3: Breaking Change (Major Version)

```bash
# Make your changes
git add .
git commit -m "[major] Restructure API with breaking changes to tool parameters"
git push origin main

# Result: 1.0.0 → 2.0.0
```

## Manual Publishing

You can also manually trigger a release from GitHub:

1. Go to **Actions** → **Publish to PyPI**
2. Click **Run workflow**
3. Select version bump type (major/minor/patch)
4. Click **Run workflow**

## Skipping CI

To push changes without triggering a release, add `[skip ci]` to your commit message:

```bash
git commit -m "Update README documentation [skip ci]"
```

This is useful for:
- Documentation updates
- README changes
- Non-code changes

## Testing Before Publishing

The `test.yml` workflow runs automatically on all pull requests and pushes:

- ✅ Code formatting checks (ruff)
- ✅ Linting (ruff)
- ✅ Type checking (mypy)
- ✅ Package structure validation
- ✅ Installation tests on Python 3.11 and 3.12

## First Time Setup

The GitHub repository is already configured with:

- ✅ `PYPI_API_TOKEN` secret (configured by you)
- ✅ GitHub Actions workflows
- ✅ Automatic versioning logic

No additional setup needed! Just push to `main` and the workflow handles everything.

## Verifying Publication

After the workflow completes:

1. **Check PyPI**: https://pypi.org/project/ultimate-gemini-mcp/
2. **Check GitHub Releases**: https://github.com/anand-92/ultimate-image-gen-mcp/releases
3. **Test Installation**:
   ```bash
   pip install ultimate-gemini-mcp --upgrade
   ```

## Troubleshooting

### Workflow Fails on Version Bump

- Check that the version format in `pyproject.toml` is valid (e.g., `1.0.0`)
- Ensure Python 3.11+ is being used

### PyPI Upload Fails

- Verify `PYPI_API_TOKEN` secret is correctly set
- Check that the token has upload permissions
- Ensure the version doesn't already exist on PyPI

### Version Not Incrementing

- Check commit message format
- Ensure `[skip ci]` is not in the commit message
- Verify the workflow actually ran (check Actions tab)

## Current Version

Current version: **1.0.0**

Next push will increment to:
- Patch: `1.0.1` (default)
- Minor: `1.1.0` (with `[minor]`)
- Major: `2.0.0` (with `[major]`)
