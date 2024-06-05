import itertools
import sys
import os
# Add the root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from pathlib import Path
import json
import csv
import logging
import timeit
import time
import datetime
from preprocess import preprocessor
import re

# with open('tmp/loader.log', 'w'):
#     pass

# Ensure the logging directory exists
tmp_dir = os.path.join(root_dir, 'tmp')
os.makedirs(tmp_dir, exist_ok=True)

log_file = os.path.join(tmp_dir, 'loader.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

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

file_with_missed_data = ['data/airlines-1565894560588.json',
                        'data/airlines-1569957146471.json',
                        'data/airlines-1573229502947.json',
                        'data/airlines-1575313134067.json',
                        'data/airlines-1570104381202.json',
                        'data/airlines-1560138591670.json',
                        'data/airlines-1560138591670.json']

def reader(path):
    with open(path) as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for line: {line}", file=sys.stderr)
                logger.error(e)
                continue
            
def csv_adder_users(data, output_file = 'users_dataset.csv'):
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

        # Iterate over the data files
        for i, path in enumerate(data):
            errors = 0
            dataset = reader(path) # Read the data file

            print(f"📍 Processing: {path}")
            start = timeit.default_timer() # Start the timer
            # Iterate over the tweets in the data file
            for j, tweet in enumerate(dataset):
                # Preprocess the tweet
                p_tweet = preprocessor.preprocess_users_in_retweeted_status(tweet)
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
                        if k not in ['text', 'coordinates', 'mentioned_airlines', 'user_mentions', 'language']:
                            v = v.replace("'", "")
                        else:
                            v = "'" + v.replace("'", "") + "'"
                        raw_values.append(v)
                        
                        # Set the values of the tweet to append to the CSV file
                        values = ", ".join(raw_values)
                        # p_tweet[k] = v

                    try:
                        # writer.writerow(p_tweet)
                        file.write(f"{values}\n") # Write the tweet to the CSV file

                    # Handle json.JSONDecodeError exceptions
                    except json.JSONDecodeError as j:
                        if path in file_with_missed_data:
                            logging.error(f"File missing. {j}")
                            pass

                    except Exception as e:
                        logging.error(f"Error: {e}, Tweet: {tweet}")
                        errors += 1
                    
                p_tweet = preprocessor.preprocessor_users(tweet)
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
                        if k not in ['text', 'coordinates', 'mentioned_airlines', 'user_mentions', 'language']:
                            v = v.replace("'", "")
                        else:
                            v = "'" + v.replace("'", "") + "'"
                        raw_values.append(v)
                        
                        # Set the values of the tweet to append to the CSV file
                        values = ", ".join(raw_values)
                        # p_tweet[k] = v

                    try:
                        # writer.writerow(p_tweet)
                        file.write(f"{values}\n") # Write the tweet to the CSV file

                    # Handle json.JSONDecodeError exceptions
                    except json.JSONDecodeError as j:
                        if path in file_with_missed_data:
                            logging.error(f"File missing. {j}")
                            logger.error(j)
                            pass

                    except Exception as e:
                        logging.error(f"Error: {e}, Tweet: {tweet}")
                        logger.error(e)
                        errors += 1
                else:
                    continue
                
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
            time_remaining = (len(data) - counter) * (elapsed / counter)
            print(f"⏯️ Process: {(counter/len(data))*100:.2f}% - #️⃣ {counter}/{len(data)} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
            print("-----------------------------------")

def csv_adder_tweets(data, output_file = 'tweets_dataset.csv'):
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
                p_tweet = preprocessor.preprocessor_tweets(tweet, tokenizer, model, configr)
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
            
# data = [Path("data/"+file) for file in os.listdir('data')]
# data.sort(key=lambda x: x.name)
# csv_adder_tweets(data)

def tweets_loader_csv(connection, path = 'combined_dataset.csv'):
    # LOAD DATA LOCAL INFILE '~/dbl_data_challenge/tweets_dataset.csv' INTO TABLE tweets FIELDS TERMINATED BY ',' ENCLOSED BY "'"  IGNORE 1 ROWS;
    query0 = """SET GLOBAL local_infile=ON;"""
    query1 = """SET FOREIGN_KEY_CHECKS=0;"""
    query = f"""
    LOAD DATA LOCAL INFILE '{path}'
    INTO TABLE tweets
    FIELDS TERMINATED BY ','
    ENCLOSED BY "'" 
    IGNORE 1 ROWS
    """
    connection.cursor().execute(query0)
    print("✅ Local infile enabled.")
    connection.cursor().execute(query1)
    print("✅ Foreign key checks disabled.")
    connection.cursor().execute(query)
    connection.commit()
    print(f"✅ {path} appended.")
    
def users_loader_csv(connection, path = 'users_dataset.csv'):
    query0 = """SET GLOBAL local_infile=ON;"""
    query1 = """SET FOREIGN_KEY_CHECKS=0;"""
    query = f"""
    LOAD DATA LOCAL INFILE '{path}'
    INTO TABLE users
    FIELDS TERMINATED BY ','
    ENCLOSED BY "'" 
    IGNORE 1 ROWS
    """
    connection.cursor().execute(query0)
    print("✅ Local infile enabled.")
    connection.cursor().execute(query1)
    print("✅ Foreign key checks disabled.")
    connection.cursor().execute(query)
    connection.commit()
    print(f"✅ {path} appended.")

def tweets_loader(connection, data):
    # Initialize variables
    elapsed = 0
    cursor = connection.cursor()

    # Iterate over the data files
    for i, path in enumerate(data):
        errors = 0
        dataset = reader(path)
        print(f"📍 Processing: {path}")
        start = timeit.default_timer()

        # Iterate over the tweets in the data file
        for j, tweet in enumerate(dataset):
            p_tweet = preprocessor.preprocessor(tweet)
            if p_tweet is not None:
                columns = ', '.join(p_tweet.keys())
                raw_values = []
                for k, v in p_tweet.items():
                    v = str(v)
                    v = re.sub(r',', '', v)
                    v = re.sub(r'http\S+', 'url_removed', v)
                    v = re.sub(r'\n', '', v)
                    if k not in ['text', 'coordinates', 'mentioned_airlines', 'user_mentions']:
                        v = v.replace("'", "")
                    else:
                        v = "'" + v.replace("'", "") + "'"
                    raw_values.append(v)
                values = ", ".join(raw_values)
                query = f"INSERT IGNORE INTO `tweets` ({columns}) VALUES ({values})"
                try:
                    cursor.execute(query)
                except Exception as e:
                    logging.error(f"Error: {e}, Tweet: {tweet}")
                    errors += 1

        # Commit the changes to the database
        connection.commit()

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
        time_remaining = (len(data) - counter) * (elapsed / counter)
        print(f"⏯️ Process: {(counter/len(data))*100:.2f}% - #️⃣ {counter}/{len(data)} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
        print("-----------------------------------")

    # Close the cursor and connection
    cursor.close()
    connection.close()

def get_languages_list(data):
    for path in data:
        dataset = reader(path)
        return {tweet['lang'] for tweet in dataset if 'lang' in tweet}

def get_deleted_tweet(data):
    for path in data:
        dataset = reader(path)
        return [tweet for tweet in dataset if 'delete' in tweet]