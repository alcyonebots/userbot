import os

# Path to store user sessions and quotes
SESSION_FILE = "sessions.json"
QUOTES_FILE = "chudai.txt"

# Load saved sessions from the file
def load_sessions():
    """Loads all user sessions from sessions.json."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            sessions = json.load(f)
        return sessions
    return {}

# Save session string for a specific user
def save_session(user_id, string_session):
    """Saves a session string for a specific user to sessions.json."""
    sessions = load_sessions()
    sessions[user_id] = string_session
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f)

# Load quotes from the chudai.txt file
def load_quotes():
    """Loads quotes from chudai.txt, each line is considered a separate quote."""
    if os.path.exists(QUOTES_FILE):
        with open(QUOTES_FILE, "r") as f:
            quotes = f.readlines()
        # Remove any extra newlines or spaces
        quotes = [quote.strip() for quote in quotes]
        return quotes
    return []

# Save quotes to chudai.txt (overwrites the file with the current list of quotes)
def save_quotes(quotes):
    """Saves the quotes to chudai.txt, each quote on a new line."""
    with open(QUOTES_FILE, "w") as f:
        for quote in quotes:
            f.write(f"{quote}\n")

# Global list of quotes (loaded at the start of the program)
quotes = load_quotes()
