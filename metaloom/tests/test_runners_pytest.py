
import pytest
import time
from metaloom.core.messages import Message

# Happy path tests
@pytest.mark.parametrize("to, title, text, expected", [
    ("user1", "Greetings", "Hello, World!", {"to": "user1", "title": "Greetings", "text": "Hello, World!"}),
    ("user2", "Update", "Your request has been processed.", {"to": "user2", "title": "Update", "text": "Your request has been processed."}),
], ids=["happy-path-greeting", "happy-path-update"])
def test_create_new_message(to, title, text, expected):
    # Act
    message = Message()
    message.create_new(to, title, text)

    # Assert
    assert message.to == expected["to"]
    assert message.title == expected["title"]
    assert message.text == expected["text"]
    assert isinstance(message.timestamp, float)

# Edge cases tests
@pytest.mark.parametrize("to, title, text", [
    ("", "", ""),  # Empty strings
    ("user3", "A" * 1000, "B" * 1000),  # Long strings
], ids=["edge-case-empty", "edge-case-long-strings"])
def test_create_new_message_edge_cases(to, title, text):
    # Act
    message = Message()
    message.create_new(to, title, text)

    # Assert
    assert message.to == to
    assert message.title == title
    assert message.text == text

# Test mark_read method
@pytest.mark.parametrize("initial_state", [True, False], ids=["read-true", "read-false"])
def test_mark_read(initial_state):
    # Arrange
    message = Message()
    message.read = initial_state

    # Act
    message.mark_read()

    # Assert
    assert message.read is True

# Test mark_unread method
@pytest.mark.parametrize("initial_state", [True, False], ids=["unread-true", "unread-false"])
def test_mark_unread(initial_state):
    # Arrange
    message = Message()
    message.read = initial_state

    # Act
    message.mark_unread()

    # Assert
    assert message.read is False



# run tests
if __name__ == "__main__":
    pytest.main()
