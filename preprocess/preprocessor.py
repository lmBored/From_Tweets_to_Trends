import re

tweets_keys = ['id',
               'text',
               'in_reply_to_status_id',
               'in_reply_to_user_id',
               'reply_count',
               'favorite_count',
               'coordinates',
               'place',
               'timestamp_ms',
               'retweet_count']

users_keys = ['id',
              'verified',
              'followers_count',
              'statuses_count']

airlines_list = ['klm',
                 'airfrance',
                 'air france',
                 'british_airways', 'british airways',
                 'americanair', 'american airlines', 'american air',
                 'lufthansa',
                 'airberlin', 'air berlin',
                 'airberlin assist', 'air berlin assist', 'airberlinassist',
                 'easyjet', 'easy jet',
                 'ryanair', 'ryan air',
                 'singaporeair', 'singapore airlines', 'singapore air',
                 'qantas',
                 'etihad airways', 'etihadairways', 'etihad',
                 'virgin atlantic', 'virginatlantic']

def text_transformer(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text) # replace repeated texts, normalization
    text = re.sub(r' 0 ', 'zero', text)
    text = re.sub(r'[^A-Za-z ]', '', text)
    text = text.lower()
    return text

def preprocessor(tweet):
    try:
        text = ''
        if 'extended_tweet' in tweet:
            text = tweet['extended_tweet']['full_text']
        elif 'text' in tweet:
            text = tweet['text']
                
        text = text_transformer(text)
                
        if 'delete' not in tweet:
            tweets_info = {k:v for k,v in tweet.items() if k in tweets_keys}
            users_info = {k:v for k,v in tweet['user'].items() if k in users_keys}
            users_info['user_id'] = users_info.pop('id')
            tweets_info.update(users_info)
            
            airlines_mentioned = [airline for airline in airlines_list if airline in text.lower()] # Need to also consider changing language
            mentioned_id = [i['id'] for i in tweet['entities']['user_mentions']]
            # text = re.sub(r'@[^ ]+', '', text) # remove username
            extended_tweets = {'text':text, 'language':tweet['lang'], 'mentioned_airlines':airlines_mentioned, 'user_mentions':mentioned_id}
            tweets_info.update(extended_tweets)
    
            nullables = ['in_reply_to_status_id', 'in_reply_to_user_id', 'coordinates', 'place']
            for i in nullables:
                if tweets_info[i] == None:
                    tweets_info[i] = 'NULL'
    
            return tweets_info
    except Exception as e:
        print(f"Error: {e}")
        return None
