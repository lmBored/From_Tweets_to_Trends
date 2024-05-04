from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

def get(key):
    return os.getenv(key)
