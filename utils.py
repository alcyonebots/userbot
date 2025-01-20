import os

def load_quotes():
    """Load quotes from a text file."""
    quotes_file = "chudai.txt"  # Path to the quotes file
    if os.path.exists(quotes_file):
        with open(quotes_file, "r") as file:
            quotes = file.readlines()
        return [quote.strip() for quote in quotes]
    return ["No text found."]
