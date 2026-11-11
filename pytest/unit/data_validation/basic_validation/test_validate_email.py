import socket
from unittest.mock import patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.data_validation]
from pyutils_collection.data_validation import validate_email


def test_validate_email_valid_emails() -> None:
    """
    Test case 1: Valid email address formats.
    """
    # Test basic valid emails
    validate_email("user@example.com")
    validate_email("test@domain.org")
    validate_email("admin@company.net")

    # Test complex valid emails
    validate_email("user.name@example.com")
    validate_email("user+tag@example.com")
    validate_email("user_123@example-domain.com")
    validate_email("first.last+tag@subdomain.example.co.uk")


def test_validate_email_subdomain_and_tld_variations() -> None:
    """
    Test case 2: Valid emails with various subdomain and TLD combinations.
    """
    # Test subdomains
    validate_email("user@mail.example.com")
    validate_email("user@sub.domain.example.org")

    # Test various TLDs
    validate_email("user@example.co.uk")
    validate_email("user@example.info")
    validate_email("user@example.museum")
    validate_email("user@example.travel")


def test_validate_email_unicode_emails() -> None:
    """
    Test case 3: Unicode email addresses when allowed.
    """
    # Test Unicode emails with allow_unicode=True
    validate_email("тест@example.com", allow_unicode=True)
    validate_email("用户@example.com", allow_unicode=True)
    validate_email("user@üñíçøðé.com", allow_unicode=True)


def test_validate_email_edge_case_valid_emails() -> None:
    """
    Test case 4: Edge cases that should be valid.
    """
    # Test minimum length email
    validate_email("a@b.co")

    # Test numbers in local part
    validate_email("123@example.com")
    validate_email("user123@example.com")

    # Test hyphens in domain
    validate_email("user@test-domain.com")
    validate_email("user@sub-domain.example-site.org")


def test_validate_email_mx_checking_success() -> None:
    """
    Test case 5: MX record validation using dnspython (success).
    """
    with patch("dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = ["mx1.example.com"]
        validate_email("user@example.com", check_mx=True)
        mock_resolve.assert_called_with("example.com", "MX")


@patch("dns.resolver.resolve", side_effect=Exception("No MX"))
@patch("socket.gethostbyname")
def test_validate_email_mx_checking_socket_fallback_success(
    mock_gethostbyname, mock_resolve
) -> None:
    """
    Test case 6: MX record validation fallback to A record (success).
    """
    mock_gethostbyname.return_value = "1.2.3.4"
    validate_email("user@example.com", check_mx=True)
    mock_gethostbyname.assert_called_with("example.com")


def test_validate_email_edge_cases() -> None:
    """
    Test case 7: Edge cases and boundary conditions.
    """
    # Test minimum valid email
    validate_email("a@b.co")

    # Test maximum local part length (64 characters)
    max_local = "a" * 64 + "@example.com"
    validate_email(max_local)

    # Test complex but valid emails
    validate_email("test.email.with+symbol@example-domain.co.uk")
    validate_email("user123+tag456@sub.domain.example.org")

    # Test numbers and hyphens
    validate_email("123@456-789.com")
    validate_email("user-name@domain-name.org")


def test_validate_email_performance_complex_emails() -> None:
    """
    Test case 8: Performance with complex email validation.
    """
    # Test performance with many validations
    emails = [
        "user1@example.com",
        "user2@domain.org",
        "test.email@subdomain.example.co.uk",
        "complex+tag@test-domain.info",
    ]

    import time

    start_time = time.time()
    for _ in range(1000):
        for email in emails:
            validate_email(email)
    elapsed_time = time.time() - start_time

    assert elapsed_time < 1.0  # Should complete within 1 second


def test_validate_email_type_error_invalid_input() -> None:
    """
    Test case 9: TypeError for non-string input.
    """
    with pytest.raises(TypeError, match="email must be str, got int"):
        validate_email(123)

    with pytest.raises(TypeError, match="email must be str, got list"):
        validate_email(["user@example.com"])

    with pytest.raises(TypeError, match="email must be str, got NoneType"):
        validate_email(None)

    # Test with custom param name
    with pytest.raises(TypeError, match="user_email must be str, got int"):
        validate_email(123, param_name="user_email")


def test_validate_email_type_error_invalid_parameters() -> None:
    """
    Test case 10: TypeError for invalid parameter types.
    """
    with pytest.raises(TypeError, match="allow_unicode must be bool, got str"):
        validate_email("user@example.com", allow_unicode="true")

    with pytest.raises(TypeError, match="check_mx must be bool, got int"):
        validate_email("user@example.com", check_mx=1)

    with pytest.raises(TypeError, match="param_name must be str, got int"):
        validate_email("user@example.com", param_name=123)


def test_validate_email_value_error_empty_email() -> None:
    """
    Test case 11: ValueError for empty email addresses.
    """
    with pytest.raises(ValueError, match="email cannot be empty"):
        validate_email("")

    # Test with custom param name
    with pytest.raises(ValueError, match="user_email cannot be empty"):
        validate_email("", param_name="user_email")


def test_validate_email_value_error_length_violations() -> None:
    """
    Test case 12: ValueError for length constraint violations.
    """
    # Test email too long (over 254 characters)
    long_email = "a" * 250 + "@example.com"
    with pytest.raises(
        ValueError, match="email exceeds maximum length of 254 characters"
    ):
        validate_email(long_email)

    # Test local part too long (over 64 characters)
    long_local = "a" * 65 + "@example.com"
    with pytest.raises(
        ValueError, match="email local part exceeds maximum length of 64 characters"
    ):
        validate_email(long_local)

    # Test domain part too long (over 253 characters)
    long_domain = "user@" + "a" * 250 + ".com"
    with pytest.raises(
        ValueError, match="email exceeds maximum length of 254 characters"
    ):
        validate_email(long_domain)


def test_validate_email_value_error_invalid_structure() -> None:
    """
    Test case 13: ValueError for invalid email structure.
    """
    # Test missing @ symbol
    with pytest.raises(ValueError, match="email must contain exactly one @ symbol"):
        validate_email("userexample.com")

    # Test multiple @ symbols
    with pytest.raises(ValueError, match="email must contain exactly one @ symbol"):
        validate_email("user@@example.com")

    with pytest.raises(ValueError, match="email must contain exactly one @ symbol"):
        validate_email("user@example@.com")

    # Test empty local part
    with pytest.raises(ValueError, match="email local part cannot be empty"):
        validate_email("@example.com")

    # Test empty domain part
    with pytest.raises(ValueError, match="email domain part cannot be empty"):
        validate_email("user@")


def test_validate_email_value_error_invalid_format() -> None:
    """
    Test case 14: ValueError for invalid email format.
    """
    # Test invalid local part format
    with pytest.raises(ValueError, match="email local part format is invalid"):
        validate_email("user..name@example.com")  # consecutive dots

    with pytest.raises(ValueError, match="email local part format is invalid"):
        validate_email(".user@example.com")  # starts with dot

    with pytest.raises(ValueError, match="email local part format is invalid"):
        validate_email("user.@example.com")  # ends with dot

    # Test invalid domain format
    with pytest.raises(ValueError, match="email domain cannot start or end with a dot"):
        validate_email("user@.example.com")  # starts with dot

    with pytest.raises(ValueError, match="email domain cannot start or end with a dot"):
        validate_email("user@example.com.")  # ends with dot

    with pytest.raises(
        ValueError, match="email domain cannot contain consecutive dots"
    ):
        validate_email("user@example..com")


def test_validate_email_value_error_domain_requirements() -> None:
    """
    Test case 15: ValueError for domain requirement violations.
    """
    # Test domain without TLD
    with pytest.raises(ValueError, match="email domain must contain at least one dot"):
        validate_email("user@localhost")

    with pytest.raises(ValueError, match="email domain must contain at least one dot"):
        validate_email("user@domain")


def test_validate_email_value_error_unicode_not_allowed() -> None:
    """
    Test case 16: ValueError for Unicode characters when not allowed.
    """
    with pytest.raises(
        ValueError, match="email contains non-ASCII characters but allow_unicode=False"
    ):
        validate_email("тест@example.com", allow_unicode=False)

    with pytest.raises(
        ValueError, match="email contains non-ASCII characters but allow_unicode=False"
    ):
        validate_email("user@üñíçøðé.com", allow_unicode=False)

    with pytest.raises(
        ValueError, match="email contains non-ASCII characters but allow_unicode=False"
    ):
        validate_email("用户@example.com")  # default allow_unicode=False


def test_validate_email_mx_checking_failure() -> None:
    """
    Test case 17: MX record validation using dnspython (failure).
    """
    # Patch dns.resolver.resolve to simulate MX record not found
    with patch("dns.resolver.resolve", side_effect=Exception("No MX")), patch(
        "socket.gethostbyname", side_effect=socket.gaierror("domain not found")
    ):
        with pytest.raises(
            ValueError,
            match="email domain does not exist|email domain does not have valid MX record",
        ):
            validate_email("user@nonexistent.com", check_mx=True)


@patch("dns.resolver.resolve", side_effect=Exception("No MX"))
@patch("socket.gethostbyname")
def test_validate_email_mx_checking_socket_fallback_failure(
    mock_gethostbyname, mock_resolve
) -> None:
    """
    Test case 18: MX record validation fallback to A record (failure).
    """
    mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")
    with pytest.raises(ValueError, match="email domain does not exist"):
        validate_email("user@nonexistent-domain-12345.com", check_mx=True)


def test_validate_email_local_part_too_long() -> None:
    """Test case 19: ValueError for local part exceeding 64 characters."""
    long_local = "a" * 65 + "@example.com"
    with pytest.raises(ValueError, match="email local part exceeds maximum length"):
        validate_email(long_local)


def test_validate_email_non_ascii_unicode_disabled() -> None:
    """Test case 20: ValueError for non-ASCII characters with allow_unicode=False."""
    with pytest.raises(
        ValueError, match="contains non-ASCII characters but allow_unicode=False"
    ):
        validate_email("tëst@example.com", allow_unicode=False)


def test_validate_email_domain_without_dot() -> None:
    """Test case 21: ValueError for domain without a dot."""
    with pytest.raises(ValueError, match="domain must contain at least one dot"):
        validate_email("user@localhost")


def test_validate_email_domain_with_consecutive_dots() -> None:
    """Test case 22: ValueError for domain with consecutive dots."""
    with pytest.raises(ValueError, match="domain cannot contain consecutive dots"):
        validate_email("user@example..com")


def test_validate_email_domain_too_long() -> None:
    """Test case 23: ValueError for email exceeding maximum length."""
    long_domain = "user@" + "a" * 254 + ".com"
    with pytest.raises(ValueError, match="email exceeds maximum length"):
        validate_email(long_domain)
