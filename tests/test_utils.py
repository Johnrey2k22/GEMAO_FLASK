import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch, MagicMock
from MyFlaskapp.utils import generate_otp, verify_otp, store_otp, validate_email, validate_password

class TestOTP:
    def test_generate_otp(self):
        """Test OTP generation."""
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    @patch('MyFlaskapp.utils.get_db_connection')
    def test_store_otp(self, mock_conn):
        """Test storing OTP in database."""
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        result = store_otp('test@example.com', '123456')
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.return_value.commit.assert_called_once()

    @patch('MyFlaskapp.utils.get_db_connection')
    def test_verify_otp_valid(self, mock_conn):
        """Test verifying valid OTP."""
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'id': 1}

        result = verify_otp('test@example.com', '123456')
        assert result is True

    @patch('MyFlaskapp.utils.get_db_connection')
    def test_verify_otp_invalid(self, mock_conn):
        """Test verifying invalid OTP."""
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = verify_otp('test@example.com', '123456')
        assert result is False

class TestValidation:
    def test_validate_email_valid(self):
        """Test valid email."""
        assert validate_email('test@example.com') is True

    def test_validate_email_invalid(self):
        """Test invalid email."""
        assert validate_email('invalid-email') is False

    def test_validate_password_valid(self):
        """Test valid password."""
        valid, msg = validate_password('ValidPass123!')
        assert valid is True

    def test_validate_password_invalid(self):
        """Test invalid password."""
        valid, msg = validate_password('short')
        assert valid is False