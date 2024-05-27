import csv
import re
from collections import Counter
import mysql.connector
from config import config

connection = mysql.connector.connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'), allow_local_infile=True)
cursor = connection.cursor()
cursor.execute("SELECT * FROM tweets ORDER BY timestamp_ms DESC")
tweets = cursor.fetchall()

word_count = Counter()

# Iterate through the tweets and update the word count
for tweet in tweets:
    text = tweet[1]
    # Remove any special characters and split by whitespace to get words
    words = re.findall(r'\b\w+\b', text.lower())
    word_count.update(words)
    
# Write the word counts to a CSV file
with open('word_counts.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Word', 'Count'])
    for word, count in word_count.items():
        csvwriter.writerow([word, count])