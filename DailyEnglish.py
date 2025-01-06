import asyncio
import requests
from dotenv import load_dotenv
from telegram import Bot
import os
from wordfreq import top_n_list
from googletrans import Translator
import random

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# API untuk mendapatkan random word dan definisi
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"


# Load English words from the `wordfreq` library
def load_words(limit=100000):
    return top_n_list("en", limit)


# Fetch a random word that hasn't been sent yet
def get_random_word(words, sent_words):
    available_words = [word for word in words if word not in sent_words]
    if available_words:
        word = random.choice(available_words)
        sent_words.add(word)  # Mark the word as sent
        return word
    return None

# Get the definition of a word
def get_definition(word):
    try:
        response = requests.get(f"{DICTIONARY_API}{word}", timeout=5)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            meaning = data[0]["meanings"][0]
            part_of_speech = meaning["partOfSpeech"]
            definition = meaning["definitions"][0]["definition"]
            # Only include example if it's available
            example = meaning["definitions"][0].get("example")

            if example:
                return f"Word: {word.capitalize()}\nPart of Speech: {part_of_speech}\nDefinition: {definition}\nExample: {example}"
            else:
                return f"Word: {word.capitalize()}\nPart of Speech: {part_of_speech}\nDefinition: {definition}"

        return f"Sorry, no definition found for the word: {word}"

    except Exception as e:
        print(f"Error fetching definition for word '{word}': {e}")
        return None


# Send a flashcard via the bot
async def send_flashcard(bot, words, sent_words):
    word = get_random_word(words, sent_words)
    if word:
        definition = get_definition(word)
        if definition:
            await bot.send_message(chat_id=CHAT_ID, text=definition)
        else:
            await bot.send_message(chat_id=CHAT_ID, text=f"Word: {word.capitalize()}")
    else:
        await bot.send_message(chat_id=CHAT_ID, text="No more words available.")

# Main loop to send flashcards every 10 seconds
async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    words = load_words(limit=100000)
    sent_words = set()  # Keep track of words already sent

    while True:
        try:
            await send_flashcard(bot, words, sent_words)
        except Exception as e:
            print(f"Error sending flashcard: {e}")
        await asyncio.sleep(60*60*3)

# Run the program
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped by user.")
