import mysql.connector
import re
from preprocess import preprocessor, reader

def tweets_loader(connection, data):
    for path in data:
        dataset = reader(path)
        for tweet in dataset:
            try:
                p_tweet = preprocessor(tweet)
                if p_tweet is not None:
                    columns = ', '.join(p_tweet.keys())
                    raw_values = []
                    for k, v in p_tweet.items():
                        v = str(v)
                        v = re.sub(r'http\S+', 'url_removed', v)
                        if k not in ['text', 'coordinates', 'place', 'language', 'mentioned_airlines', 'user_mentions']:
                            v = v.replace("'", "")
                        else:
                            v = f"'{v.replace("'", "")}'"
                        raw_values.append(v)
                    values = ", ".join(raw_values)
                    query = "INSERT INTO `tweets` (%s) VALUES (%s)" % (columns, values)
                    insert = connection.cursor().execute(query)
            except Exception as e:
                print(f"Error: {e}")
                pass
        connection.commit()

def users_loader(connection, data):
    for path in data:
        dataset = reader(path)
        for tweet in dataset:
            try:
                p_tweet = preprocessor(tweet)
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
                print(f"Error: {e}")
                pass
        connection.commit()
