import torch
import numpy as np
from scipy.special import softmax
import re
import timeit
import logging
import json
import itertools
import csv
import datetime
from pathlib import Path

#================================================================================================

import asyncio
import aiofiles
from concurrent.futures import ProcessPoolExecutor

#================================================================================================

import nest_asyncio
nest_asyncio.apply()

#================================================================================================

import sys
import os

# Add the root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Ensure the logging directory exists
tmp_dir = os.path.join(root_dir, 'tmp')
os.makedirs(tmp_dir, exist_ok=True)

log_file = os.path.join(tmp_dir, 'tweets_loader.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

#================================================================================================

from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
# import time

from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
configr = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
# device = torch.device('mps' if torch.cuda.is_available() else 'cpu')
model.to(device)

#================================================================================================

file_with_missed_data = ['data/airlines-1565894560588.json',
                        'data/airlines-1569957146471.json',
                        'data/airlines-1573229502947.json',
                        'data/airlines-1575313134067.json',
                        'data/airlines-1570104381202.json',
                        'data/airlines-1560138591670.json',
                        'data/airlines-1560138591670.json']

airlines_dict = {"KLM": 56377143 ,
                "AirFrance": 106062176 ,
                "British_Airways": 18332190 ,
                "AmericanAir": 22536055 ,
                "Lufthansa": 124476322 ,
                "AirBerlin": 26223583 ,
                "AirBerlin assist": 2182373406 ,
                "easyJet": 38676903 ,
                "RyanAir": 1542862735 ,
                "SingaporeAir": 253340062 ,
                "Qantas": 218730857 ,
                "EtihadAirways": 45621423 ,
                "VirginAtlantic": 20626359
                }

tweets_keys = ['id',
                'text',
                'in_reply_to_status_id',
                'coordinates',
                'timestamp_ms',
                'quoted_status_id']

users_keys = ['id',
            'verified',
            'followers_count',
            'statuses_count']

airlines_list_dict = {"KLM":  ['klm'],
                    "AirFrance":  ['airfrance', 'air france'],
                    "British_Airways":  ['british_airways', 'british airways'],
                    "AmericanAir":  ['americanair', 'american airlines', 'american air'],
                    "Lufthansa":  ['lufthansa'],
                    "AirBerlin":  ['airberlin', 'air berlin'],
                    "AirBerlin assist":  ['airberlin assist', 'air berlin assist', 'airberlinassist'],
                    "easyJet":  ['easyjet', 'easy jet'],
                    "RyanAir":  ['ryanair', 'ryan air'],
                    "SingaporeAir":  ['singaporeair', 'singapore airlines', 'singapore air'],
                    "Qantas":  ['qantas'],
                    "EtihadAirways":  ['etihad airways', 'etihadairways', 'etihad'],
                    "VirginAtlantic":  ['virgin atlantic', 'virginatlantic']}

languages_list = ['en', 'de', 'es', 'fr', 'nl', 'it']

#================================================================================================

def transform_text(text):
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1\1', text) # replace repeated texts, normalization
    text = re.sub(r'[^A-Za-z0-9]+', '', text) # remove special characters
    text = re.sub(r'@\S+', '@user', text) # replace user mentions
    return text

def roberta(text, tokenizer, model, configr):
    ptext = transform_text(text)
    
    input = tokenizer(ptext, return_tensors='pt')
    input = input.to(device)
    
    with torch.no_grad():
        output = model(**input)
        
    scores = output[0][0].cpu().detach().numpy()
    scores = softmax(scores)
    
    sentiment_score = scores[2].item() - scores[0].item()
    max_score = np.argmax(scores)
    label = configr.id2label[max_score]
    
    return label, sentiment_score


def roberta_batch(texts, tokenizer, model, configr):
    ptexts = [transform_text(text) for text in texts]
    
    inputs = tokenizer(ptexts, return_tensors='pt', padding=True, truncation=True)
    inputs = inputs.to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    scores = outputs.logits.cpu().numpy()
    scores = softmax(scores, axis=1)
    
    labels = [configr.id2label[np.argmax(score)] for score in scores]
    sentiment_scores = [score[2] - score[0] for score in scores]
    
    return labels, sentiment_scores

#================================================================================================

def text_transformer(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r' 0 ', 'zero', text) # replace 0 with zero
    # text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text) # replace repeated texts, normalization
    # text = re.sub(r'[^A-Za-z ]', '', text) # remove special characters
    text = re.sub(r'\n', '', text)
    text = re.sub(r'[,.!?]', '', text)
    text = text.strip()
    text = text.lower()
    return text

def preprocess_tweet(tweet):
    try:
        if 'delete' not in tweet:
            text = tweet['text']
            if 'retweeted_status' in tweet:
                if 'extended_tweet' in tweet['retweeted_status']:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']  # Get the full text from the extended tweet
                
            text = text_transformer(text)  # Apply text transformation

            tweets_info = {k: 0 if k in ['id', 'in_reply_to_status_id', 'timestamp_ms', 'quoted_status_id'] else 'NULL' for k in tweets_keys}
            tweets_info.update({k: v for k, v in tweet.items() if k in tweets_keys})
            
            tweets_info['user_id'] = tweet['user']['id']

            if 'coordinates' in tweet and tweet['coordinates'] is not None:
                tweets_info['coordinates'] = str(tweet['coordinates']['coordinates'])
                tweets_info['coordinates'] = re.sub(r'[\[\]]', '', tweets_info['coordinates'])
                tweets_info['coordinates'] = re.sub(r',', ' and ', tweets_info['coordinates'])
            
            lang = tweet['lang'] if 'lang' in tweet else 'und'
            if lang not in languages_list:
                return None, None
            
            airlines_mentioned = [airline for airline in airlines_list_dict for i in airlines_list_dict[airline] if i in text.lower()]
            
            mentioned_id = [i['id'] for i in tweet['entities']['user_mentions']] if tweet.get('entities') and tweet['entities'].get('user_mentions') else []
            
            extended_tweets = {'text': text, 'language': lang, 'mentioned_airlines': airlines_mentioned, 'user_mentions': mentioned_id}
            tweets_info.update(extended_tweets)
        
            if 'retweeted_status' in tweet:
                retweeted_status = {'id': 0}
                retweeted_status.update({k: v for k, v in tweet['retweeted_status'].items() if k in ['id']})
                retweeted_status['retweeted_status_id'] = retweeted_status.pop('id')
                
                if 'user' in tweet['retweeted_status']:
                    retweeted_status['retweeted_status_user_id'] = tweet['retweeted_status']['user']['id']
                else:
                    retweeted_status['retweeted_status_user_id'] = 0
                
                for i in retweeted_status:
                    if retweeted_status[i] is None:
                        retweeted_status[i] = 'NULL'
                tweets_info.update(retweeted_status)
            else:
                retweeted_status = {'retweeted_status_id': 0, 'retweeted_status_user_id': 0}
                tweets_info.update(retweeted_status)
                        
            nullables_int = ['in_reply_to_status_id', 'quoted_status_id']
            for i in nullables_int:
                if tweets_info[i] is None:
                    tweets_info[i] = 0
                    
            nullables = ['coordinates']
            for i in nullables:
                if tweets_info[i] is None:
                    tweets_info[i] = 'NULL'

            return tweets_info, text
            
    except Exception as e:
        logging.error(f"Error: {e}")
        return None, None
    
#================================================================================================

async def reader(path):
    async with aiofiles.open(path, mode='r') as f:
        async for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for line: {line}", file=sys.stderr)
                logging.error(e)
                continue

async def async_preprocess_tweet(executor, tweet):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, preprocess_tweet, tweet)
            
async def csv_adder_tweets(data, output_file='tweets_dataset_gpu.csv', batch_size=32):
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"📛 {output_file} already exists and has contents. Overwrite? [y/n]")
        while True:
            choice = input()
            if choice == 'y':
                break
            elif choice == 'n':
                return
            else:
                print("Invalid choice.")

    async with aiofiles.open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = None
        elapsed = 0
        length_data = len(data)

        with ProcessPoolExecutor() as executor:
            for i, path in enumerate(data):
                errors = 0
                tweets = []
                
                async for tweet in reader(path):
                    tweets.append(tweet)
                
                n = len(tweets)
                
                print(f"📍 Processing: {path}")
                
                start = timeit.default_timer()
                elapsed_per_tweet = 0
                tweet_batch = []

                for j, tweet in enumerate(tweets):
                    start_per_tweet = timeit.default_timer()
                    tweet_batch.append(tweet)

                    if len(tweet_batch) == batch_size or j == n - 1:
                        preprocess_tasks = [async_preprocess_tweet(executor, tweet) for tweet in tweet_batch]
                        preprocessed_tweets = await asyncio.gather(*preprocess_tasks)
                        
                        preprocessed_tweets = [item for item in preprocessed_tweets if isinstance(item, tuple) and len(item) == 2]
                        
                        try:
                            valid_tweets = [(pt, text) for pt, text in preprocessed_tweets if pt is not None and text is not None]
                        except Exception as e:
                            print(f"Error: {e}")
                            logger.error(e)
                        texts = [text for pt, text in valid_tweets]

                        if texts:
                            labels, scores = roberta_batch(texts, tokenizer, model, configr)
                            
                            for (pt, _), label, score in zip(valid_tweets, labels, scores):
                                if pt:
                                    pt['label'] = label
                                    pt['score'] = score

                                    if writer is None:
                                        writer = csv.DictWriter(file, fieldnames=pt.keys())
                                        await writer.writeheader()
                                    
                                    raw_values = []
                                    for k, v in pt.items():
                                        v = str(v)
                                        v = re.sub(r',', '', v)
                                        v = re.sub(r'http\S+', 'url_removed', v)
                                        v = re.sub(r'\n', '', v)
                                        v = v.strip()
                                        if k not in ['text', 'coordinates', 'mentioned_airlines', 'user_mentions', 'language']:
                                            v = v.replace("'", "")
                                        else:
                                            v = "'" + v.replace("'", "") + "'"
                                        raw_values.append(v)
                                    
                                    values = ",".join(raw_values)
                                    try:
                                        await file.write(f"{values}\n")
                                    except json.JSONDecodeError as jso:
                                        logging.error(f"File missing. {jso}")
                                    except Exception as e:
                                        logging.error(f"Error: {e}, Tweet: {tweet}")
                                        errors += 1
                                        
                                    finally:
                                        duration_per_tweet = timeit.default_timer() - start_per_tweet
                                        counter_per_tweet = j + 1
                                        elapsed_per_tweet += duration_per_tweet
                                        time_remaining_per_tweet = (n - counter_per_tweet) * (elapsed_per_tweet / counter_per_tweet)
                                        print(f"🛝 Process: {(counter_per_tweet/n)*100:.2f}% - #️⃣ {counter_per_tweet}/{n} tweets processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining_per_tweet))}", end='\r')
                                        sys.stdout.flush()
                        tweet_batch = []

                print()
                duration = timeit.default_timer() - start

                if errors == 0:
                    print(f"✅ {path} appended.")
                else:
                    print(f"❌ {path} not appended processed - {errors} exceptions ignored.", file=sys.stderr)

                counter = i + 1
                elapsed += duration
                time_remaining = (length_data - counter) * (elapsed / counter)
                print(f"⏯️ Process: {(counter/length_data)*100:.2f}% - #️⃣ {counter}/{length_data} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
                print("-----------------------------------")

if __name__ == "__main__":
    data = [Path("data/"+file) for file in os.listdir('data')]
    asyncio.run(csv_adder_tweets(data))