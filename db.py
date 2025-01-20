import pymongo
import os

# MongoDB setup
client = pymongo.MongoClient("mongodb+srv://Cenzo:Cenzo123@cenzo.azbk1.mongodb.net/")
db = client["reaper"]
sessions_collection = db["sessions"]

# Load quotes from a file
def load_quotes():
    quotes_file = 'chudai.txt'
    if os.path.exists(quotes_file):
        with open(quotes_file, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return ["No quotes found."]

quotes = load_quotes()
