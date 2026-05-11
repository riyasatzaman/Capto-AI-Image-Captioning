# Marks this directory as pytest's rootdir so test files can `import app`
# without a sys.path hack. Without this, pytest walks up from tests/, finds
# no __init__.py, and uses tests/ itself as the import root.
