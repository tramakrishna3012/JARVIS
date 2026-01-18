"""
Basic tests for JARVIS backend
"""

import pytest


def test_app_imports():
    """Test that the main app can be imported"""
    from app.main import app
    assert app is not None


def test_config_loads():
    """Test that config loads successfully"""
    from app.core.config import settings
    assert settings.APP_NAME == "JARVIS"


def test_models_import():
    """Test that all models can be imported"""
    from app.models import User, Profile, Job, Resume, Application, Referral, Email
    assert User is not None
    assert Profile is not None
    assert Job is not None
    assert Resume is not None
    assert Application is not None
    assert Referral is not None
    assert Email is not None
