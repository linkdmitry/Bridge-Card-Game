# Global message log for the game
message_log = []
max_messages = 50  # Keep only the last 50 messages

def display_message(message):
    """Display a message to the user and store it in the message log."""
    print(message)
    
    # Add message to the log with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    
    message_log.append(formatted_message)
    
    # Keep only the last max_messages
    if len(message_log) > max_messages:
        message_log.pop(0)

def get_messages():
    """Get all messages from the log."""
    return message_log.copy()

def clear_messages():
    """Clear all messages from the log."""
    global message_log
    message_log = []

def validate_input(user_input, valid_options):
    """Validate user input against a list of valid options."""
    return user_input in valid_options

def format_card_info(card):
    """Format the card information for display."""
    return f"{card.rank} of {card.suit}"