import sys

def check_python_version():
    """
    Checks if the current Python version is supported.
    Currently, Python 3.14+ is not supported due to incompatibilities
    in the 'chromadb' dependency with Pydantic v1.
    """
    if sys.version_info >= (3, 14):
        print("\033[91m" + "="*80 + "\033[0m")
        print("\033[91mERROR: Semantic Backup Explorer is currently not compatible with Python 3.14 or greater.\033[0m")
        print("\nThis is due to an incompatibility in the 'chromadb' dependency, which relies on ")
        print("Pydantic v1. Pydantic v1 core functionality is broken on Python 3.14+.")
        print("\nPlease use a supported Python version: 3.10, 3.11, 3.12, or 3.13.")
        print("\033[91m" + "="*80 + "\033[0m")
        sys.exit(1)
