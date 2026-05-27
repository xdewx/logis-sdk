# Generate version
python scripts/build.py

# Clean pycache
Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Clean old builds
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# Build
python setup.py sdist bdist_wheel

# Check
twine check dist/*

Write-Host "To upload to PyPI, run: twine upload dist/*"
Write-Host "To upload to test PyPI, run: twine upload --repository testpypi dist/*"
