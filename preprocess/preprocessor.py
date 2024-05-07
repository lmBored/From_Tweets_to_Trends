import re
import logging

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

languages_list = ['en', 'es', 'fr', 'nl', 'de', 'ja', 'ko', 'it']

def text_transformer(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text) # replace repeated texts, normalization
    text = re.sub(r' 0 ', 'zero', text)
    text = re.sub(r'[^A-Za-z ]', '', text)
    text = re.sub(r'\n', '', text)
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
            tweets_info = {k:0 if k in ['id', 'in_reply_to_status_id', 'in_reply_to_user_id', 'reply_count', 'retweet_count', 'favorite_count',
                                        'timestamp_ms'] else 'NULL' for k in tweets_keys}
            tweets_info.update({k:v for k,v in tweet.items() if k in tweets_keys})

            if 'coordinates' in tweet and tweet['coordinates'] != None:
                tweets_info['coordinates'] = str(tweet['coordinates']['coordinates'])
                tweets_info['coordinates'] = re.sub(r'[\[\]]', '', tweets_info['coordinates'])
                tweets_info['coordinates'] = re.sub(r',', ' and ', tweets_info['coordinates'])
    
            users_info = {'id': 0, 'verified':0, 'followers_count':0, 'statuses_count':0}
            users_info.update({k:v for k,v in tweet['user'].items() if k in users_keys})
            if users_info['verified'] == True:
                users_info['verified'] = 1
            else:
                users_info['verified'] = 0
            users_info['user_id'] = users_info.pop('id')
            tweets_info.update(users_info)
            
            airlines_mentioned = [airline for airline in airlines_list if airline in text.lower()] # Need to also consider changing language
            mentioned_id = [i['id'] for i in tweet['entities']['user_mentions']]
            # text = re.sub(r'@[^ ]+', '', text) # remove username
            lang = tweet['lang']
            if ('lang' in tweet and tweet['lang'] == None) or 'lang' not in tweet:
                lang = 'und'
            if lang not in languages_list:
                return None
            extended_tweets = {'text':text, 'language':lang, 'mentioned_airlines':airlines_mentioned, 'user_mentions':mentioned_id}
            tweets_info.update(extended_tweets)
    
            if 'retweeted_status' in tweet:
                retweeted_status = {'retweeted_status_id': 0, 'retweeted_status_text': 'NULL'}
                retweeted_status.update({k:v for k,v in tweet['retweeted_status'].items() if k in ['id', 'text']})
    
                if 'user' in tweet['retweeted_status']:
                    user_in_retweeted_status = {'id': 0, 'verified':0, 'followers_count':0, 'statuses_count':0}
                    user_in_retweeted_status.update({k:v for k,v in tweet['retweeted_status']['user'].items() if k in users_keys})
                    if user_in_retweeted_status['verified'] == True:
                        user_in_retweeted_status['verified'] = 1
                    else:
                        user_in_retweeted_status['verified'] = 0
                    user_in_retweeted_status['retweeted_status_user_id'] = user_in_retweeted_status.pop('id')
                    user_in_retweeted_status['retweeted_status_verified'] = user_in_retweeted_status.pop('verified')
                    user_in_retweeted_status['retweeted_status_followers_count'] = user_in_retweeted_status.pop('followers_count')
                    user_in_retweeted_status['retweeted_status_statuses_count'] = user_in_retweeted_status.pop('statuses_count')
                else:
                    user_in_retweeted_status = {'retweeted_status_user_id': 0,
                                                'retweeted_status_verified':0,
                                                'retweeted_status_followers_count':0,
                                                'retweeted_status_statuses_count':0}
                
                retweeted_status.update(user_in_retweeted_status)
                for i in retweeted_status:
                    if retweeted_status[i] == None:
                        retweeted_status[i] == 'NULL'
                tweets_info.update(retweeted_status)
            else:
                retweeted_status = {'retweeted_status_id': 0, 'retweeted_status_text': 'NULL'}
                user_in_retweeted_status = {'retweeted_status_user_id': 0,
                                            'retweeted_status_verified':0,
                                            'retweeted_status_followers_count':0,
                                            'retweeted_status_statuses_count':0}
                retweeted_status.update(user_in_retweeted_status)
                tweets_info.update(retweeted_status)
    
            nullables_int = ['in_reply_to_status_id', 'in_reply_to_user_id', ]
            for i in nullables_int:
                if tweets_info[i] == None:
                    tweets_info[i] = 0
                    
            nullables = ['coordinates']
            for i in nullables:
                if tweets_info[i] == None:
                    tweets_info[i] = 'NULL'
                    
            return tweets_info
            
    except Exception as e:
        logging.error(f"Error: {e}")
        return None