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
                        if k not in ['text', 'coordinates', 'mentioned_airlines', 'user_mentions']:
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
                        if k not in ['text', 'coordinates', 'mentioned_airlines', 'user_mentions', 'retweeted_status_text']:
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

        # Iterate over the data files
        for i, path in enumerate(data):
            errors = 0
            dataset = reader(path) # Read the data file

            print(f"📍 Processing: {path}")
            start = timeit.default_timer() # Start the timer
            # Iterate over the tweets in the data file
            for j, tweet in enumerate(dataset):
                # Preprocess the tweet
                p_tweet = preprocessor.preprocessor_tweets(tweet)
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
                        if k not in ['text', 'coordinates', 'mentioned_airlines', 'user_mentions', 'retweeted_status_text']:
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

def tweets_loader_csv(connection, data, path = 'tweets_dataset.csv'):
    # LOAD DATA LOCAL INFILE '~/dbl_data_challenge/tweets_dataset.csv' INTO TABLE tweets FIELDS TERMINATED BY ',' ENCLOSED BY "'"  IGNORE 1 ROWS;
    query1 = """SET FOREIGN_KEY_CHECKS=0;"""
    query = f"""
    LOAD DATA LOCAL INFILE '{path}'
    INTO TABLE tweets
    FIELDS TERMINATED BY ','
    ENCLOSED BY "'" 
    IGNORE 1 ROWSs
    """
    connection.cursor().execute(query1)
    print("✅ Foreign key checks disabled.")
    connection.cursor().execute(query)
    connection.commit()
    print(f"✅ {path} appended.")
    
def users_loader_csv(connection, data, path = 'users_dataset.csv'):
    query = f"""
    LOAD DATA LOCAL INFILE '{path}'
    INTO TABLE users
    FIELDS TERMINATED BY ','
    ENCLOSED BY "'" 
    IGNORE 1 ROWS
    """
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