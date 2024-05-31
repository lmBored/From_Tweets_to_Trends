from sentiment_score import *
import pandas as pd
import mysql.connector

# Establish database connection
connection = mysql.connector.connect(host='localhost', user='root', password='',database='jbg030', allow_local_infile=True)

# Fetch column names for the tweets table
cursor = connection.cursor()
cursor.execute("SHOW COLUMNS FROM tweets")
columns = cursor.fetchall()
tweet_columns = [col[0] for col in columns]
tweet_columns_str = ','.join([f'tweets.{col}' for col in tweet_columns])

print(tweet_columns_str)

def get_queries(airline):
    # Query for the conversation ID's for conversation with that airline
    conv = f'''
       SELECT conversation_id
       FROM conversations
       WHERE airline LIKE %{airline}%';
    '''
    # Query for all tweets where the airline is mentioned
    mentioned = f'''
       SELECT * 
       FROM tweets
       WHERE mentioned_airlines LIKE '%{airline}%';
    '''
    return conv, mentioned

# This will return a table with all the tweets from the conversations with an given airline
def get_table_airline(airline):
    conv, mentioned = get_queries(airline)

    # We somehow need to combine the conv query and the query below, but I don't know how to do it right now so please help
    query_tweets_conv = f'''
       SELECT {tweet_columns_str}
       FROM tweets, conversations
       JOIN hasher ON tweets.id = hasher.id
       JOIN conversations ON hasher.conversation_id = conversations.conversation_id;
    '''

    # After we have obtained all the tweets belonging to a conversation and all the tweets where the airline is mentioned, we join the tables
    join_tables = 'tbd'
    df_airline = join_tables

    # Then, we remove all duplicates
    df_airline = df_airline # but then without duplicates

    return df_airline

