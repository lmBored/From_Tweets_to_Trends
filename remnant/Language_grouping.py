from langdetect import detect, LangDetectException
import mysql.connector
from config import config

connection = mysql.connector.connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'), allow_local_infile=True)

cursor = connection.cursor()
cursor.execute("SELECT * FROM tweets ORDER BY timestamp_ms DESC")
tweets = cursor.fetchall()

langdict = {}
for tweet in tweets:
    try:
        lang_detected = detect(tweet[1])
    except LangDetectException:
        lang_detected = "unknown"
        continue
    if lang_detected != tweet[7].strip():
        if lang_detected == 'nl':
            print(tweet[1])
            print(f"Detected: {lang_detected} | Stored: {tweet[7].strip()}")
            print("----------")
        if lang_detected in langdict:
            if tweet[7].strip() not in langdict[lang_detected]:
                langdict[lang_detected].append(tweet[7].strip())
        else:
            langdict[lang_detected] = list()
            
print(langdict)