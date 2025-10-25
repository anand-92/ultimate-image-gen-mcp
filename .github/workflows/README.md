# GitHub Actions Workflows

## Publish to PyPI

The `publish.yml` workflow automatically versions and publishes the package to PyPI.

### Automatic Versioning

The workflow automatically increments the version based on commit messages:

- **Patch bump** (default): `1.0.0` → `1.0.1`
  - Used for bug fixes and minor changes
  - No special keyword needed

- **Minor bump**: `1.0.0` → `1.1.0`
  - Add `[minor]` to your commit message
  - Used for new features

- **Major bump**: `1.0.0` → `2.0.0`
  - Add `[major]` to your commit message
  - Used for breaking changes

### Examples

```bash
# Patch version (1.0.0 → 1.0.1)
git commit -m "Fix image saving bug"
git push origin main

# Minor version (1.0.0 → 1.1.0)
git commit -m "[minor] Add support for new aspect ratios"
git push origin main

# Major version (1.0.0 → 2.0.0)
git commit -m "[major] Complete API redesign with breaking changes"
git push origin main
```

### Manual Trigger

You can also manually trigger a release from the GitHub Actions tab:

1. Go to Actions → Publish to PyPI
2. Click "Run workflow"
3. Select the version bump type (major/minor/patch)
4. Click "Run workflow"

### What Happens

When you push to main:

1. ✅ Detects version bump type from commit message
2. ✅ Increments version in `pyproject.toml` and `src/__init__.py`
3. ✅ Commits the version bump with `[skip ci]` to avoid infinite loops
4. ✅ Creates a git tag (e.g., `v1.0.1`)
5. ✅ Builds the Python package
6. ✅ Publishes to PyPI using `PYPI_API_TOKEN` secret
7. ✅ Creates a GitHub Release with changelog

### Requirements

- `PYPI_API_TOKEN` secret must be configured in repository settings
- Python 3.11+ for building
- uv for fast builds and dependency management

### Skipping CI

To prevent the workflow from running on a commit, add `[skip ci]` to the commit message:

```bash
git commit -m "Update README [skip ci]"
```

This is automatically added to version bump commits to prevent infinite loops.
