import os
import sys

# Ensure the repository root is on sys.path so tests can import the MyFlaskapp package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from MyFlaskapp import create_app

@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "SESSION_COOKIE_SECURE": False,
        "SESSION_COOKIE_HTTPONLY": False
    })
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

if __name__ == '__main__':
    import subprocess
    
    print("Running pytest with this conftest.py configuration...")
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], cwd=ROOT)
    sys.exit(result.returncode)
