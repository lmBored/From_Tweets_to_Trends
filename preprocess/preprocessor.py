import re

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

languages_list = ['ar','ca','cs','cy','da','de','el','en','es','et','fa','fi','fr','hi','ht','hu','in','it',
                  'iw','ja','ko','lt','nl','no','pl','pt','ro','ru','sv','th','tl','tr','uk','und','ur','zh']

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
    
            if 'retweeted_status' in tweet:
                retweeted_status = {}
                retweeted_status['retweeted_status'] = {k:v for k,v in tweet['retweeted_status'].items() if k in ['id', 'text']}
                user_in_retweeted_status = {k:v for k,v in tweet['retweeted_status']['user'].items() if k in users_keys}
                user_in_retweeted_status['user_id'] = user_in_retweeted_status.pop('id')
                retweeted_status['retweeted_status'].update(user_in_retweeted_status)
                tweets_info.update(retweeted_status)
            else:
                tweets_info['retweeted_status'] = 'NULL'
    
            nullables = ['in_reply_to_status_id', 'in_reply_to_user_id', 'coordinates', 'place', 'retweeted_status']
            for i in nullables:
                if tweets_info[i] == None:
                    tweets_info[i] = 'NULL'
    
            return tweets_info
            
    except Exception as e:
        logging.error(f"Error: {e}")
        return None
