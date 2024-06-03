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
import mysql.connector

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

from config import config

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

# languages_list = ['en', 'de', 'es', 'fr', 'nl', 'it']
languages_list = ['en']

#================================================================================================

def transform_text(text):
    text = text.lower()  # Normalize case
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1\1', text)  # Replace repeated characters
    text = re.sub(r'@\S+', '@user', text)  # Replace user mentions
    text = re.sub(r'#', '', text)  # Optional: Remove the hashtag symbol, keep the word
    text = re.sub(r'[^a-z0-9 ]+', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
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

def preprocessor_tweets(tweet, tokenizer, model, configr):
    try:
        if 'delete' not in tweet:
            lang = tweet['lang']  # Get the language of the tweet
            # Set language as 'und' if it is not specified
            if ('lang' in tweet and tweet['lang'] == None) or 'lang' not in tweet:
                lang = 'und'  # Set language as 'und' if it is not specified

            if lang not in languages_list:
                return None  # Return None if the language is not in the supported languages
            
            # start_time = time.time()
            # Get the text from the tweet
            text = tweet['text']
            if 'retweeted_status' in tweet:
                if 'extended_tweet' in tweet['retweeted_status']:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']  # Get the full text from the extended tweet
                
            text = text_transformer(text)  # Apply text transformation

            # Initialize a dictionary to store tweet information
            tweets_info = {k:0 if k in ['id', 'in_reply_to_status_id', 'timestamp_ms', 'quoted_status_id'] else 'NULL' for k in tweets_keys}
            tweets_info.update({k:v for k,v in tweet.items() if k in tweets_keys})  # Update the dictionary with tweet information
            
            tweets_info['user_id'] = tweet['user']['id']

            if 'coordinates' in tweet and tweet['coordinates'] != None:
                # Format the coordinates as a string
                tweets_info['coordinates'] = str(tweet['coordinates']['coordinates'])
                tweets_info['coordinates'] = re.sub(r'[\[\]]', '', tweets_info['coordinates'])
                tweets_info['coordinates'] = re.sub(r',', ' and ', tweets_info['coordinates'])

            # Initialize a list to store mentioned airlines
            airlines_mentioned = []
            for airline in airlines_list_dict:
                for i in airlines_list_dict[airline]:
                    if i in text.lower():
                        airlines_mentioned.append(airline)  # Add mentioned airlines to the list
            
            # Initialize a list to store mentioned user IDs
            mentioned_id = []
            if tweet.get('entities') and tweet['entities'].get('user_mentions'):  # Check if 'entities' and 'user_mentions' exist and are not None
                mentioned_id = [i['id'] for i in tweet['entities']['user_mentions']]  # Get the IDs of mentioned users
            
            label, score = roberta(text, tokenizer, model, configr)
                
            # Initialize a dictionary to store extended tweet information
            # extended_tweets = {'text':text, 'language':lang, 'mentioned_airlines':airlines_mentioned, 'user_mentions':mentioned_id}
            extended_tweets = {'text': text, 'language': lang, 'mentioned_airlines': airlines_mentioned, 'user_mentions': mentioned_id, 'label': label, 'score': score}
            tweets_info.update(extended_tweets)  # Update the tweet information dictionary with extended tweet information
        
            if 'retweeted_status' in tweet:
                # Initialize a dictionary to store retweeted status information
                retweeted_status = {'id': 0}
                retweeted_status.update({k:v for k,v in tweet['retweeted_status'].items() if k in ['id']})  # Update the dictionary with retweeted status information
                retweeted_status['retweeted_status_id'] = retweeted_status.pop('id')
                
                if 'user' in tweet['retweeted_status']:
                    retweeted_status['retweeted_status_user_id'] = tweet['retweeted_status']['user']['id']
                else:
                    retweeted_status['retweeted_status_user_id'] = 0
                
                # Set none values to 'NULL'
                for i in retweeted_status:
                    if retweeted_status[i] == None:
                        retweeted_status[i] == 'NULL'
                tweets_info.update(retweeted_status)  # Update the tweet information dictionary with retweeted status information

            else: # 'retweeted_status' not in tweet
                # Initialize a dictionary to store retweeted status information
                retweeted_status = {'retweeted_status_id': 0, 'retweeted_status_user_id': 0}
                tweets_info.update(retweeted_status)  # Update the tweet information dictionary with retweeted status information
                        
            # Set nullable integer values to 0
            nullables_int = ['in_reply_to_status_id', 'quoted_status_id']
            for i in nullables_int:
                if tweets_info[i] == None:
                    tweets_info[i] = 0  # Set nullable integer values to 0
                    
            # Set nullable boolean values to 0
            nullables = ['coordinates']
            for i in nullables:
                if tweets_info[i] == None:
                    tweets_info[i] = 'NULL'  # Set nullable values to 'NULL'

            # print(f"Preprocessor time taken: {time.time() - start_time}")
            
            return tweets_info  # Return the processed tweet information
            
    except Exception as e:
        logging.error(f"Error: {e}")  # Log the error
        logger.error(e)
        return None  # Return None in case of an error
    
#================================================================================================

def reader(path):
    with open(path) as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for line: {line}", file=sys.stderr)
                logger.error(e)
                continue
            
def csv_adder_tweets(data, name, output_file = None):
    # Set the output file name
    if output_file is None:
        output_file = f'tweets_dataset_{name}.csv'
        
    # Check if the output file already exists and has contents
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"📛 {output_file} already exists and has contents. Overwrite? [y/n]")
        while True:
            # Ask the user if they want to overwrite the file
            choice = input()
            if choice == 'y':
                break
            elif choice == 'n':
                return
            else:
                print("Invalid choice.")

    # Open the output file in write mode
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = None
        elapsed = 0
        length_data = len(data)

        # Iterate over the data files
        for i, path in enumerate(data):
            errors = 0
            dataset, dataset0 = itertools.tee(reader(path)) # Read the data file
            n = sum(1 for _ in dataset0) # Count the number of tweets in the data file
            print(f"📍 Processing: {path}")
            
            start = timeit.default_timer() # Start the timer
            elapsed_per_tweet = 0
            for j, tweet in enumerate(dataset): # Iterate over the tweets in the data file
                start_per_tweet = timeit.default_timer()
                # Preprocess the tweet
                p_tweet = preprocessor_tweets(tweet, tokenizer, model, configr)
                if p_tweet is not None:
                    # Write the header row if it doesn't exist
                    if writer is None:
                        writer = csv.DictWriter(file, fieldnames=p_tweet.keys())
                        writer.writeheader()
                    
                    # Initialize a list to store the raw values
                    raw_values = []         
                    for k, v in p_tweet.items():
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
                        
                        # Set the values of the tweet to append to the CSV file
                        values = ",".join(raw_values)
                        # p_tweet[k] = v

                    try:
                        # writer.writerow(p_tweet)
                        file.write(f"{values}\n") # Write the tweet to the CSV file

                    # Handle json.JSONDecodeError exceptions
                    except json.JSONDecodeError as jso:
                        if path in file_with_missed_data:
                            logging.error(f"File missing. {jso}")
                            logger.error(jso)
                            pass

                    except Exception as e:
                        logging.error(f"Error: {e}, Tweet: {tweet}")
                        logger.error(e)
                        errors += 1
                        
                    finally:
                        duration_per_tweet = timeit.default_timer() - start_per_tweet
                        counter_per_tweet = j + 1
                        elapsed_per_tweet += duration_per_tweet
                        time_remaining_per_tweet = (n - counter_per_tweet) * (elapsed_per_tweet / counter_per_tweet)
                        print(f"🛝 Process: {(counter_per_tweet/n)*100:.2f}% - #️⃣ {counter_per_tweet}/{n} tweets processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining_per_tweet))}", end='\r')
                        sys.stdout.flush()
                else:
                    continue
            print()
                
            # Calculate the duration of the process
            duration = timeit.default_timer() - start

            # Print the status of the process
            if errors == 0:
                print(f"✅ {path} appended.")
            else:
                print(f"❌ {path} not appended processed - {errors} exceptions ignored.", file=sys.stderr)

            # Print the progress of the process
            counter = i + 1
            elapsed += duration
            time_remaining = (length_data - counter) * (elapsed / counter)
            print(f"⏯️ Process: {(counter/length_data)*100:.2f}% - #️⃣ {counter}/{length_data} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
            print("-----------------------------------")
            
name = input("Name? (khoi, ilse, illija, oliver, jan, sven) :")

if name == 'khoi':
    lines = [0, 95]
elif name == 'ilse':
    lines = [95, 190]
elif name == 'illija':
    lines = [190, 285]
elif name == 'oliver':
    lines = [285, 380]
elif name == 'jan':
    lines = [380, 475]
elif name == 'sven':
    lines = [475, 567]
    
files = []
with open('json_files.txt') as file:
    for i, line in enumerate(file):
        if lines[0] <= i < lines[1]:
            files.append(line.strip())

data = [Path("data/"+file) for file in os.listdir('data') if file in files]

connection = mysql.connector.connect(host='localhost', user='root', password=config.get('PASSWORD'),database='jbg030', allow_local_infile=True)

csv_adder_tweets(data, name)