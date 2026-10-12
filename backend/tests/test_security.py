from app.core.security import hash_password, hash_token, verify_password


def test_password_hash_is_not_plaintext():
    stored = hash_password("s3cret-password")
    assert "s3cret-password" not in stored
    assert stored.startswith("scrypt$")


def test_password_verify():
    stored = hash_password("s3cret-password")
    assert verify_password("s3cret-password", stored) is True
    assert verify_password("wrong-password", stored) is False


def test_password_salt_unique():
    assert hash_password("same") != hash_password("same")


def test_token_hash_deterministic():
    assert hash_token("abc") == hash_token("abc")
    assert hash_token("abc") != hash_token("abcd")
