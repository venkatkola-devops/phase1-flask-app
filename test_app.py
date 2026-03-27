"""
tests/test_app.py

Basic smoke tests for the Flask app.
These run in Stage 2 of the Jenkins pipeline.
"""

import sys
import os

# Add parent directory to path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_imports():
    """Test that the app file imports without crashing"""
    import app  # noqa
    assert True


def test_health_route(monkeypatch):
    """Test the /health endpoint returns 200"""
    # We mock the database so we don't need a real MySQL connection in tests
    import app as flask_app
    flask_app.app.config["TESTING"] = True

    with flask_app.app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
