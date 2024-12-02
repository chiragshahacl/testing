from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pytest

from app.auth.crypto import (
    JWTClaims,
    decode_token,
    get_access_token,
    hash_password,
    verify_password,
)
from app.auth.enums import RoleNames
from app.auth.models import Role, User
from app.settings import config


@pytest.fixture
def mock_config():
    """Mock the configuration settings."""
    with patch.object(config, "JWT_AUDIENCE", "test_audience"), patch.object(
        config, "JWT_ISSUER", "test_issuer"
    ), patch.object(config, "JWT_DURATION_MINUTES", 60):
        yield


def test_hash_password():
    """Test that hashing a password returns a valid hash."""
    password = "secure_password"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_verify_password_match():
    """Test that verifying a matching password returns (True, needs_rehash)."""
    password = "secure_password"
    hashed = hash_password(password)
    match, needs_rehash = verify_password(password, hashed)
    assert match is True
    assert needs_rehash is False


def test_verify_password_no_match():
    """Test that verifying a non-matching password returns (False, False)."""
    password = "secure_password"
    hashed = hash_password(password)
    match, needs_rehash = verify_password("wrong_password", hashed)
    assert match is False
    assert needs_rehash is False


def test_verify_password_needs_rehash():
    """Test that a password hash needing rehash is identified."""
    password = "secure_password"
    with patch("argon2.PasswordHasher.check_needs_rehash", return_value=True):
        hashed = hash_password(password)
        match, needs_rehash = verify_password(password, hashed)
        assert match is True
        assert needs_rehash is True


def test_get_access_token(mock_config):
    """Test that generating an access token returns a valid JWT."""
    mock_role = MagicMock(spec=Role)
    mock_role.name = "admin"
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.roles = [mock_role]

    token = get_access_token(mock_user)
    assert isinstance(token, str)
    decoded = jwt.decode(
        token,
        config.JWT_VERIFYING_KEY,
        audience=config.JWT_AUDIENCE,
        algorithms=[config.JWT_ALGORITHM],
    )
    assert decoded["sub"] == "1"
    assert decoded["username"] == "testuser"
    assert decoded["roles"] == ["admin"]
    assert decoded["aud"] == "test_audience"
    assert decoded["iss"] == "test_issuer"


def test_decode_token_valid(mock_config):
    """Test that decoding a valid token returns the expected claims."""
    claims = JWTClaims(
        sub="1",
        nbf=datetime.now(UTC).timestamp(),
        exp=(datetime.now(UTC) + timedelta(minutes=60)).timestamp(),
        username="testuser",
        roles=[RoleNames.ADMIN],
    )
    token = jwt.encode(
        payload=claims.model_dump(),
        key=config.JWT_SIGNING_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    decoded_claims = decode_token(token)
    assert decoded_claims
    assert decoded_claims.sub == "1"
    assert decoded_claims.username == "testuser"
    assert decoded_claims.roles == ["admin"]


def test_decode_token_expired(mock_config):
    """Test that decoding an expired token returns None."""
    claims = JWTClaims(
        sub="1",
        nbf=datetime.now(UTC).timestamp(),
        exp=(datetime.now(UTC) - timedelta(minutes=1)).timestamp(),
        username="testuser",
        roles=["admin"],
    )
    token = jwt.encode(
        payload=claims.model_dump(),
        key=config.JWT_SIGNING_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    decoded_claims = decode_token(token)
    assert decoded_claims is None
