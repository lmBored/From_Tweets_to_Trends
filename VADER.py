from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import time

# Initialize the SentimentIntensity Analyzer
analyzer = SentimentIntensityAnalyzer()


# Read the dataset
df_tweets = pd.read_csv('tweets_dataset.csv', lineterminator='\n')

# Create copies of dataframe 
df_tweets_sentiment = df_tweets.copy()

# Define the ranges (can still be changed)
lowerbound = -0.5
upperbound = 0.5

# Start the timer for processing data
start = time.time()

# Analyze the text and assign scores
for i in range(len(df_tweets_sentiment)):

    # Analyze the text
    scores = analyzer.polarity_scores(df_tweets_sentiment.loc[i, 'text'])

    # Create new columns with all the sentiment values
    df_tweets_sentiment.loc[i, 'negative'] = scores['neg']
    df_tweets_sentiment.loc[i, 'neutral'] = scores['neu']
    df_tweets_sentiment.loc[i, 'positive'] = scores['pos']
    df_tweets_sentiment.loc[i, 'compound'] = scores['compound']

    # Define the sentiment of the text
    if scores['compound'] <= lowerbound:
        df_tweets_sentiment.loc[i, 'sentiment'] = 'negative'
    elif scores['compound'] >= upperbound:
        df_tweets_sentiment.loc[i, 'sentiment'] = 'positive'
    else:
        df_tweets_sentiment.loc[i, 'sentiment'] = 'neutral'

    if (i + 1) % 10 == 0:
        elapsed_time = time.time() - start
        time_per_iteration = elapsed_time / (i + 1)
        remaining_it = len(df_tweets_sentiment) - (i + 1)
        estimated_time = time_per_iteration * remaining_it
        print(f"Processed {i + 1}/{len(df_tweets_sentiment)} rows. Estimated time remaining: {estimated_time/60:.2f} minutes")
        
print("loading completed")