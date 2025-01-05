import asyncio
import requests
from dotenv import load_dotenv
from telegram import Bot
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# API untuk mendapatkan random word dan definisi
RANDOM_WORD_API = "https://random-word-api.herokuapp.com/word?number=1"
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"

# Fungsi untuk mendapatkan random word
def get_random_word():
    try:
        response = requests.get(RANDOM_WORD_API, timeout=5)
        response.raise_for_status()
        word = response.json()
        return word[0]
    except Exception as e:
        print(f"Error fetching random word: {e}")
        return None

# Fungsi untuk mendapatkan definisi kata
def get_definition(word):
    try:
        response = requests.get(f"{DICTIONARY_API}{word}", timeout=5)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            meaning = data[0]["meanings"][0]
            part_of_speech = meaning["partOfSpeech"]
            definition = meaning["definitions"][0]["definition"]
            return f"Word: {word}\nPart of Speech: {part_of_speech}\nDefinition: {definition}"
        else:
            return f"Sorry, no definition found for the word: {word}"
    except Exception as e:
        print(f"Error fetching definition for word '{word}': {e}")
        return None

# Fungsi untuk mengirim flashcard
async def send_flashcard(bot):
    word = get_random_word()
    if word:
        card = get_definition(word)
        if card:
            await bot.send_message(chat_id=CHAT_ID, text=card)
        # else:
        #     await bot.send_message(chat_id=CHAT_ID, text="Sorry, unable to fetch the definition.")
    # else:
    #     await bot.send_message(chat_id=CHAT_ID, text="Sorry, unable to fetch a random word.")

# Main loop untuk mengirim flashcard tiap 10 detik
async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    while True:
        try:
            await send_flashcard(bot)
        except Exception as e:
            print(f"Error sending flashcard: {e}")
        await asyncio.sleep(3)  # Delay 10 detik

# Jalankan program
asyncio.run(main())
