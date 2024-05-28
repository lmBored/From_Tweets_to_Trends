import sys
sys.path.append('../dbl_data_challenge')
from config import config
import mysql.connector
import timeit
import datetime
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from multiprocessing import Pool, cpu_count

# Load the tokenizer and model once
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")

def sentiment_score(text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    score = (probabilities[0][2].item() - probabilities[0][0].item())
    return score

def process_batch(batch):
    connection = connection = mysql.connector.connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'), allow_local_infile=True)
    cursor = connection.cursor()
    results = []
    for tweet in batch:
        id, text = tweet
        try:
            score = sentiment_score(text)
            results.append((id, score))
        except Exception as e:
            print(f"❌ Error: {e}, Tweet: {id}", file=sys.stderr)
    cursor.executemany("UPDATE `tweets` SET `sentiment` = %s WHERE `id` = %s", results)
    connection.commit()
    cursor.close()
    connection.close()

def update_sentiment_scores(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT `id`, `text` FROM `tweets`")
    tweets = cursor.fetchall()
    cursor.close()
    connection.close()

    batch_size = 1000
    batches = [tweets[i:i + batch_size] for i in range(0, len(tweets), batch_size)]

    with Pool(cpu_count()) as pool:
        pool.map(process_batch, batches)

    print(f"✅ All tweets processed and updated.")