import sys
import os
import json
import csv
import logging
import timeit
import datetime
from preprocess import preprocessor
import re

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
            except json.JSONDecodeError:
                print(f"Error decoding JSON for line: {line}", file=sys.stderr)
                continue

def csv_adder(data, output_file = 'dataset.csv'):
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
    with open(output_file, 'w', newline='') as file:
        writer = None
        elapsed = 0
        for i, path in enumerate(data):
            errors = 0
            dataset = reader(path)
            print(f"📍 Processing: {path}")
            start = timeit.default_timer()
            for j, tweet in enumerate(dataset):
                p_tweet = preprocessor.preprocessor(tweet)
                if p_tweet is not None:
                    if writer is None:
                        writer = csv.DictWriter(file, fieldnames=p_tweet.keys())
                        writer.writeheader()
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
                        # p_tweet[k] = v
                    try:
                        # writer.writerow(p_tweet)
                        file.write(f"{values}\n")
                    except json.JSONDecodeError as j:
                        if path in file_with_missed_data:
                            logging.error(f"File missing. {j}")
                            pass
                    except Exception as e:
                        logging.error(f"Error: {e}, Tweet: {tweet}")
                        errors += 1
                    
            duration = timeit.default_timer() - start
            if errors == 0:
                print(f"✅ {path} appended.")
            else:
                print(f"❌ {path} not appended processed - {errors} exceptions ignored.", file=sys.stderr)
            counter = i + 1
            elapsed += duration
            time_remaining = (len(data) - counter) * (elapsed / counter)
            print(f"⏯️ Process: {(counter/len(data))*100:.2f}% - #️⃣ {counter}/{len(data)} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
            print("-----------------------------------")

def tweets_loader_csv(connection, data, path = 'dataset.csv'):
    query = f"""
    LOAD DATA LOCAL INFILE '{path}'
    INTO TABLE tweets
    FIELDS TERMINATED BY ','
    ENCLOSED BY "'" 
    IGNORE 1 ROWS
    """
    connection.cursor().execute(query)
    connection.commit()
    print(f"✅ {path} appended.")

def tweets_loader(connection, data):
    elapsed = 0
    cursor = connection.cursor()
    for i, path in enumerate(data):
        errors = 0
        dataset = reader(path)
        print(f"📍 Processing: {path}")
        start = timeit.default_timer()
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
        connection.commit()
        duration = timeit.default_timer() - start
        if errors == 0:
            print(f"✅ {path} appended.")
        else:
            print(f"❌ {path} not appended processed - {errors} exceptions ignored.", file=sys.stderr)
        counter = i + 1
        elapsed += duration
        time_remaining = (len(data) - counter) * (elapsed / counter)
        print(f"⏯️ Process: {(counter/len(data))*100:.2f}% - #️⃣ {counter}/{len(data)} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
        print("-----------------------------------")
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