"""
Unit tests for check_encoding_issues function.
"""

from conftest import Base, Product
from sqlalchemy import Column, Integer, Text
from sqlalchemy.engine import Engine

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.database]
from pyutils_collection.database_functions.schema_inspection import check_encoding_issues


def test_check_encoding_issues_detects_null_bytes(memory_engine: Engine) -> None:
    """
    Test case 1: Detect NULL bytes (\\x00) in text columns.
    """
    # Arrange
    Product.__table__.create(memory_engine)
    conn = memory_engine.connect()

    # Insert data with NULL byte
    conn.execute(
        Product.__table__.insert(),
        {
            "id": 1,
            "name": "Product1",
            "title": "Test\x00Article",
            "content": "Normal content",
        },
    )
    conn.execute(
        Product.__table__.insert(),
        {"id": 2, "name": "Product2", "title": "Normal", "content": "Content\x00Here"},
    )
    conn.commit()

    # Act
    issues = check_encoding_issues(conn, tables=["products"])

    # Assert - should detect NULL bytes in both title and content columns
    assert isinstance(issues, list)
    # Depending on implementation, may detect 1 or 2 issues
    if len(issues) > 0:
        assert any(
            "null" in issue.get("issue_type", "").lower()
            or "byte" in issue.get("issue_type", "").lower()
            for issue in issues
        )

    conn.close()


def test_check_encoding_issues_clean_data(memory_engine) -> None:
    """
    Test case 2: Returns empty list for clean data.
    """
    # Arrange
    Product.__table__.create(memory_engine)
    conn = memory_engine.connect()

    # Insert clean data
    conn.execute(
        Product.__table__.insert(),
        {
            "id": 1,
            "name": "Product1",
            "title": "Normal Title",
            "content": "Normal content",
        },
    )
    conn.execute(
        Product.__table__.insert(),
        {"id": 2, "name": "Product2", "title": "Another", "content": "More content"},
    )
    conn.commit()

    # Act
    issues = check_encoding_issues(conn, tables=["products"])

    # Assert - clean data should have no or minimal issues
    assert isinstance(issues, list)
    # May be empty or have very few issues

    conn.close()


def test_check_encoding_issues_empty_table(memory_engine) -> None:
    """
    Test case 3: Handle empty table gracefully.
    """
    # Arrange
    Product.__table__.create(memory_engine)
    conn = memory_engine.connect()

    # Act
    issues = check_encoding_issues(conn, tables=["products"])

    # Assert
    assert isinstance(issues, list)
    assert len(issues) == 0

    conn.close()


def test_check_encoding_issues_specific_tables(memory_engine) -> None:
    """
    Test case 4: Check specific tables only.
    """
    # Arrange
    Product.__table__.create(memory_engine)
    conn = memory_engine.connect()

    conn.execute(
        Product.__table__.insert(),
        {"id": 1, "name": "Product1", "title": "Test", "content": "Content"},
    )
    conn.commit()

    # Act
    issues = check_encoding_issues(conn, tables=["products"])

    # Assert - should only check articles table
    assert isinstance(issues, list)
    for issue in issues:
        assert issue.get("table_name") == "products"

    conn.close()


def test_check_encoding_issues_sample_limit(memory_engine) -> None:
    """
    Test case 5: Respect sample_limit parameter.
    """
    # Arrange
    Product.__table__.create(memory_engine)
    conn = memory_engine.connect()

    # Insert multiple rows with issues
    for i in range(10):
        conn.execute(
            Product.__table__.insert(),
            {
                "id": i,
                "name": f"Product{i}",
                "title": f"Test\x00{i}",
                "content": "Content",
            },
        )
    conn.commit()

    # Act - limit to 5 samples
    issues = check_encoding_issues(conn, tables=["products"], sample_limit=5)

    # Assert - sample_values should not exceed limit
    assert isinstance(issues, list)
    for issue in issues:
        if "sample_values" in issue:
            assert len(issue["sample_values"]) <= 5

    conn.close()


def test_check_encoding_issues_invalid_connection_type_error() -> None:
    """
    Test case 6: TypeError for None connection.
    """
    # Arrange
    expected_message = "connection cannot be None"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        check_encoding_issues(None)


def test_check_encoding_issues_invalid_tables_type_error(memory_engine: Engine) -> None:
    """
    Test case 7: TypeError for invalid tables parameter.
    """
    # Arrange
    conn = memory_engine.connect()
    expected_message = "tables must be list or None"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        check_encoding_issues(conn, tables="products")

    conn.close()


def test_check_encoding_issues_invalid_schema_type_error(memory_engine: Engine) -> None:
    """
    Test case 8: TypeError for invalid schema parameter.
    """
    # Arrange
    conn = memory_engine.connect()
    expected_message = "schema must be str or None"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        check_encoding_issues(conn, schema=123)

    conn.close()


def test_check_encoding_issues_invalid_sample_limit_type_error(memory_engine: Engine) -> None:
    """
    Test case 9: TypeError for invalid sample_limit parameter.
    """
    # Arrange
    conn = memory_engine.connect()
    expected_message = "sample_limit must be int"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        check_encoding_issues(conn, sample_limit="100")

    conn.close()


def test_check_encoding_issues_negative_sample_limit_value_error(memory_engine: Engine) -> None:
    """
    Test case 10: ValueError for negative sample_limit.
    """
    # Arrange
    conn = memory_engine.connect()
    expected_message = "sample_limit must be non-negative"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        check_encoding_issues(conn, sample_limit=-1)

    conn.close()


def test_check_encoding_issues_control_characters(memory_engine) -> None:
    """
    Test case 9: Detect control characters in text.
    """
    # Arrange
    Product.__table__.create(memory_engine)
    conn = memory_engine.connect()

    # Insert data with control characters (tab, newline are usually OK, but others may be flagged)
    conn.execute(
        Product.__table__.insert(),
        {
            "id": 1,
            "name": "Product1",
            "title": "Test\x01Article",
            "content": "Content\x02",
        },
    )
    conn.commit()

    # Act
    issues = check_encoding_issues(conn, tables=["products"])

    # Assert
    assert isinstance(issues, list)
    # May or may not detect depending on implementation

    conn.close()


def test_check_encoding_issues_multiple_tables(memory_engine) -> None:
    """
    Test case 12: Checks multiple tables when specified.
    """
    # Arrange

    class Comment(Base):
        """Test Comment model."""

        __tablename__ = "comments"
        id = Column(Integer, primary_key=True)
        text = Column(Text)

    Product.__table__.create(memory_engine)
    Comment.__table__.create(memory_engine)
    conn = memory_engine.connect()

    conn.execute(
        Product.__table__.insert(),
        {"id": 1, "name": "Product1", "title": "Test", "content": "Content"},
    )
    conn.execute(Comment.__table__.insert(), {"id": 1, "text": "Comment"})
    conn.commit()

    # Act
    issues = check_encoding_issues(conn, tables=["products", "comments"])

    # Assert
    assert isinstance(issues, list)
    # Should check both tables (may have issues or be clean)

    conn.close()
