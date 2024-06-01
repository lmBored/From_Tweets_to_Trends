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
    # Query for all tweets where the airline is mentioned
    mentioned = f'''
       SELECT * 
       FROM tweets
       WHERE mentioned_airlines LIKE '%{airline}%';
    '''
    return mentioned

# This will return a table with all the tweets from the conversations with an given airline
def get_table_airline(airline):
    query_mentioned = get_queries(airline)

    query_tweets_conv = f'''
       SELECT {tweet_columns_str}
       FROM tweets
       JOIN hasher ON tweets.id = hasher.id
       JOIN conversations ON hasher.conversation_id = conversations.conversation_id
       WHERE conversations.conversation_id IN (
           SELECT conv.conversation_id
           FROM conversations AS conv
           WHERE conv.airline LIKE '%{airline}%'
       )
    '''

    df_airline_conv = pd.read_sql(query_tweets_conv, connection)
    df_airline_ment = pd.read_sql(query_mentioned, connection)

    # After we have obtained all the tweets belonging to a conversation and all the tweets where the airline is mentioned, we join the tables
    df_all_tweets = pd.concat([df_airline_conv, df_airline_ment], ignore_index=True)

    # Then, we remove all duplicates
    df_airline = df_all_tweets.drop_duplicates()

    return df_airline

get_table_airline('KLM')

def choose_airline():
    airline = input('Choose KLM, British Airways, Lufthansa or AirFrance (and type it in the exact same way) ')
    if airline == 'British Airways':
        airline = 'British_Airways'

    return get_table_airline(airline)

#choose_airline()