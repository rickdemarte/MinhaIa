import sys
import unittest
from pathlib import Path

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import API  # noqa: E402


class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.original_auth_enabled = API.AUTH_ENABLED
        self.original_owner = API.VALID_OWNER
        self.original_keys = list(API.VALID_KEYS)

    def tearDown(self):
        API.AUTH_ENABLED = self.original_auth_enabled
        API.VALID_OWNER = self.original_owner
        API.VALID_KEYS = self.original_keys

    def test_validate_token_is_optional_when_security_is_disabled(self):
        API.AUTH_ENABLED = False

        owner = API.validate_token(None)

        self.assertEqual(owner, "anonymous")

    def test_validate_token_requires_credentials_when_security_is_enabled(self):
        API.AUTH_ENABLED = True

        with self.assertRaises(HTTPException) as ctx:
            API.validate_token(None)

        self.assertEqual(ctx.exception.status_code, 401)

    def test_validate_token_accepts_valid_credentials(self):
        API.AUTH_ENABLED = True
        API.VALID_OWNER = "henrique"
        API.VALID_KEYS = ["secret"]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="henrique:secret")

        owner = API.validate_token(credentials)

        self.assertEqual(owner, "henrique")


if __name__ == "__main__":
    unittest.main()
