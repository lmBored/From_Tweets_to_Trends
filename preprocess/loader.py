import sys
import json
import csv
import logging
import timeit
import datetime
import preprocessor

def reader(path):
    with open(path) as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for line: {line}", file=sys.stderr)
                continue

def csv_adder(data, output_file = 'dataset.csv'):
    with open(output_file, 'w', newline='') as file:
        writer = None
        elapsed = 0
        for i, path in enumerate(data):
            errors = 0
            dataset = reader(path)
            print(f"📍 Processing: {path}")
            start = timeit.default_timer()
            for j, tweet in enumerate(dataset):
                p_tweet = preprocessor(tweet)
                if p_tweet is not None:
                    if writer is None:
                        writer = csv.DictWriter(file, fieldnames=p_tweet.keys())
                        writer.writeheader()
                    
                    for k, v in p_tweet.items():
                        v = str(v)
                        v = re.sub(r'http\S+', 'url_removed', v)
                        if k not in ['text', 'coordinates', 'place', 'language', 'mentioned_airlines', 'user_mentions', 'retweeted_status']:
                            v = v.replace("'", "")
                        else:
                            v = f'"{v.replace("'", "")}"'
                        p_tweet[k] = v
                    try:
                        writer.writerow(p_tweet)
                    except JSONDecodeError as j:
                        if path == 'data/airlines-1565894560588.json':
                            logging.error(f"File missing. {j}")
                            pass
                    except Exception as e:
                        logging.error(f"Error: {e}, Tweet: {tweet}")
                        errors += 1
                    
            duration = timeit.default_timer() - start
            if errors == 0:
                print(f"✅ {path} appended.")
            else:
                print(f"❌ {path} not appended processed - {errors} exceptions ignored.", file=stderr)
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

def tweets_loader(connection, data):
    elapsed = 0
    cursor = connection.cursor()
    for i, path in enumerate(data):
        errors = 0
        dataset = reader(path)
        print(f"📍 Processing: {path}")
        start = timeit.default_timer()
        for j, tweet in enumerate(dataset):
            p_tweet = preprocessor(tweet)
            if p_tweet is not None:
                columns = ', '.join(p_tweet.keys())
                raw_values = []
                for k, v in p_tweet.items():
                    v = str(v)
                    v = re.sub(r'http\S+', 'url_removed', v)
                    if k not in ['text', 'coordinates', 'place', 'language', 'mentioned_airlines', 'user_mentions', 'retweeted_status']:
                        v = v.replace("'", "")
                    else:
                        v = f'"{v.replace("'", "")}"'
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
            print(f"❌ {path} not appended processed - {errors} exceptions ignored.", file=stderr)
        counter = i + 1
        elapsed += duration
        time_remaining = (len(data) - counter) * (elapsed / counter)
        print(f"⏯️ Process: {(counter/len(data))*100:.2f}% - #️⃣ {counter}/{len(data)} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
        print("-----------------------------------")

def users_loader(connection, data):
    for path in data:
        dataset = reader(path)
        for tweet in dataset:
            try:
                p_tweet = preprocessor.preprocessor(tweet)
                if p_tweet is not None:
                    columns = ', '.join([k for k in ('user_id', 'verified', 'followers_count', 'statuses_count') if k in p_tweet.keys()])
                    raw_values = []
                    for k in ['user_id', 'verified', 'followers_count', 'statuses_count']:
                        if k in p_tweet:
                            v = str(p_tweet[k])
                            v = re.sub(r'http\S+', 'url_removed', v)
                            raw_values.append(v)
                    values = ", ".join(raw_values)
                    query = "INSERT INTO `users` (%s) VALUES (%s)" % (columns, values)
                    insert = connection.cursor().execute(query)
            except Exception as e:
                logging.error(f"Error: {e}")
                pass
        connection.commit()

def get_languages_list(data):
    for path in data:
        dataset = reader(path)
        return {tweet['lang'] for tweet in dataset if 'lang' in tweet}

def get_deleted_tweet(data):
    for path in data:
        dataset = reader(path)
        return [tweet for tweet in dataset if 'delete' in tweet]


