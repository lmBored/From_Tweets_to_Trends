import re
import logging
# import time
# from googletrans import Translator

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
                'coordinates',
                'timestamp_ms',
                'quoted_status_id']

users_keys = ['id',
            'verified',
            'followers_count',
            'statuses_count']

airlines_list_dict = {"KLM":  ['klm'],
                    "AirFrance":  ['airfrance', 'air france'],
                    "British_Airways":  ['british_airways', 'british airways'],
                    "AmericanAir":  ['americanair', 'american airlines', 'american air'],
                    "Lufthansa":  ['lufthansa'],
                    "AirBerlin":  ['airberlin', 'air berlin'],
                    "AirBerlin assist":  ['airberlin assist', 'air berlin assist', 'airberlinassist'],
                    "easyJet":  ['easyjet', 'easy jet'],
                    "RyanAir":  ['ryanair', 'ryan air'],
                    "SingaporeAir":  ['singaporeair', 'singapore airlines', 'singapore air'],
                    "Qantas":  ['qantas'],
                    "EtihadAirways":  ['etihad airways', 'etihadairways', 'etihad'],
                    "VirginAtlantic":  ['virgin atlantic', 'virginatlantic']}

languages_list = ['en', 'de', 'es', 'fr', 'in', 'nl', 'it', 'pt']

def text_transformer(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r' 0 ', 'zero', text) # replace 0 with zero
    # text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text) # replace repeated texts, normalization
    # text = re.sub(r'[^A-Za-z ]', '', text) # remove special characters
    text = re.sub(r'\n', '', text) 
    text = text.lower()
    return text

def preprocessor_users(tweet):
    try:
        if 'delete' not in tweet:
            # Initialize a dictionary to store user information
            users_info = {'id': 0, 'verified':0, 'followers_count':0, 'statuses_count':0}
            users_info.update({k:v for k,v in tweet['user'].items() if k in users_keys})  # Update the dictionary with user information

            # Set boolean values to 0 or 1
            if users_info['verified'] == True:
                users_info['verified'] = 1
            else:
                users_info['verified'] = 0

            # Rename the keys
            users_info['user_id'] = users_info.pop('id')
            
            return users_info  # Return the processed tweet information
            
    except Exception as e:
        logging.error(f"Error: {e}")  # Log the error
        return None  # Return None in case of an error

def preprocess_users_in_retweeted_status(tweet):
    try:
        if 'delete' not in tweet:
            if 'retweeted_status' in tweet:
                if 'user' in tweet['retweeted_status']:
                    # Initialize a dictionary to store user information in the retweeted status
                    user_in_retweeted_status = {'id': 0, 'verified':0, 'followers_count':0, 'statuses_count':0}
                    user_in_retweeted_status.update({k:v for k,v in tweet['retweeted_status']['user'].items() if k in users_keys})  # Update the dictionary with user information
                    
                    # Set boolean values to 0 or 1
                    if user_in_retweeted_status['verified'] == True:
                        user_in_retweeted_status['verified'] = 1
                    else:
                        user_in_retweeted_status['verified'] = 0

                    # Rename the keys
                    user_in_retweeted_status['user_id'] = user_in_retweeted_status.pop('id')

                else: # 'user' not in tweet['retweeted_status']
                    return None
                
                return user_in_retweeted_status
            
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

def preprocessor_tweets(tweet):
    try:
        if 'delete' not in tweet:
            # start_time = time.time()
            # Get the text from the tweet
            text = tweet['text']
            if 'retweeted_status' in tweet:
                if 'extended_tweet' in tweet['retweeted_status']:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']  # Get the full text from the extended tweet
                
            text = text_transformer(text)  # Apply text transformation

            # Initialize a dictionary to store tweet information
            tweets_info = {k:0 if k in ['id', 'in_reply_to_status_id', 'timestamp_ms', 'quoted_status_id'] else 'NULL' for k in tweets_keys}
            tweets_info.update({k:v for k,v in tweet.items() if k in tweets_keys})  # Update the dictionary with tweet information
            
            tweets_info['user_id'] = tweet['user']['id']

            if 'coordinates' in tweet and tweet['coordinates'] != None:
                # Format the coordinates as a string
                tweets_info['coordinates'] = str(tweet['coordinates']['coordinates'])
                tweets_info['coordinates'] = re.sub(r'[\[\]]', '', tweets_info['coordinates'])
                tweets_info['coordinates'] = re.sub(r',', ' and ', tweets_info['coordinates'])
            
            lang = tweet['lang']  # Get the language of the tweet
            # Set language as 'und' if it is not specified
            if ('lang' in tweet and tweet['lang'] == None) or 'lang' not in tweet:
                lang = 'und'  # Set language as 'und' if it is not specified

            if lang not in languages_list:
                return None  # Return None if the language is not in the supported languages
            
            # Translate the text to English
            # translator = Translator()
            # if text.strip() == '':
            #     text = 'NULL'

            # translated_text = text
            # if lang == 'ko' or lang == 'ja':
            #     translated_text = translator.translate(text, dest='en').text
            #     if tweets_info['id'] == 1135698097001062400:
            #         print(translated_text)

            # Initialize a list to store mentioned airlines
            airlines_mentioned = []
            for airline in airlines_list_dict:
                for i in airlines_list_dict[airline]:
                    if i in text.lower():
                        airlines_mentioned.append(airline)  # Add mentioned airlines to the list
            
            # Initialize a list to store mentioned user IDs
            mentioned_id = []
            if tweet.get('entities') and tweet['entities'].get('user_mentions'):  # Check if 'entities' and 'user_mentions' exist and are not None
                mentioned_id = [i['id'] for i in tweet['entities']['user_mentions']]  # Get the IDs of mentioned users
                
            # score = sentiment_score.roberta(text)  # Get the sentiment score of the tweet
                
            # Initialize a dictionary to store extended tweet information
            extended_tweets = {'text':text, 'language':lang, 'mentioned_airlines':airlines_mentioned, 'user_mentions':mentioned_id}
            tweets_info.update(extended_tweets)  # Update the tweet information dictionary with extended tweet information
        
            if 'retweeted_status' in tweet:
                # Initialize a dictionary to store retweeted status information
                retweeted_status = {'id': 0, 'text': 'NULL'}
                retweeted_status.update({k:v for k,v in tweet['retweeted_status'].items() if k in ['id', 'text']})  # Update the dictionary with retweeted status information
                retweeted_status['text'] = text_transformer(retweeted_status['text'])  # Apply text transformation
                retweeted_status['retweeted_status_id'] = retweeted_status.pop('id')
                retweeted_status['retweeted_status_text'] = retweeted_status.pop('text')

                # if 'user' in tweet['retweeted_status']:
                #     # Initialize a dictionary to store user information in the retweeted status
                #     user_in_retweeted_status = {'id': 0, 'verified':0, 'followers_count':0, 'statuses_count':0}
                #     user_in_retweeted_status.update({k:v for k,v in tweet['retweeted_status']['user'].items() if k in users_keys})  # Update the dictionary with user information
                    
                #     # Set boolean values to 0 or 1
                #     if user_in_retweeted_status['verified'] == True:
                #         user_in_retweeted_status['verified'] = 1
                #     else:
                #         user_in_retweeted_status['verified'] = 0

                #     # Rename the keys
                #     user_in_retweeted_status['retweeted_status_user_id'] = user_in_retweeted_status.pop('id')
                #     user_in_retweeted_status['retweeted_status_verified'] = user_in_retweeted_status.pop('verified')
                #     user_in_retweeted_status['retweeted_status_followers_count'] = user_in_retweeted_status.pop('followers_count')
                #     user_in_retweeted_status['retweeted_status_statuses_count'] = user_in_retweeted_status.pop('statuses_count')

                # else: # 'user' not in tweet['retweeted_status']
                #     user_in_retweeted_status = {'retweeted_status_user_id': 0,
                #                                 'retweeted_status_verified':0,
                #                                 'retweeted_status_followers_count':0,
                #                                 'retweeted_status_statuses_count':0}
                # retweeted_status.update(user_in_retweeted_status) # Update the dictionary with user information
                
                if 'user' in tweet['retweeted_status']:
                    retweeted_status['retweeted_status_user_id'] = tweet['retweeted_status']['user']['id']
                else:
                    retweeted_status['retweeted_status_user_id'] = 0
                
                # Set none values to 'NULL'
                for i in retweeted_status:
                    if retweeted_status[i] == None:
                        retweeted_status[i] == 'NULL'
                tweets_info.update(retweeted_status)  # Update the tweet information dictionary with retweeted status information

            else: # 'retweeted_status' not in tweet
                # Initialize a dictionary to store retweeted status information
                retweeted_status = {'retweeted_status_id': 0, 'retweeted_status_text': 'NULL', 'retweeted_status_user_id': 0}
                # Initialize a dictionary to store user information in the retweeted status
                # user_in_retweeted_status = {'retweeted_status_user_id': 0,
                #                             'retweeted_status_verified':0,
                #                             'retweeted_status_followers_count':0,
                #                             'retweeted_status_statuses_count':0}
                # retweeted_status.update(user_in_retweeted_status) # Update the dictionary with user information
                tweets_info.update(retweeted_status)  # Update the tweet information dictionary with retweeted status information
                        
            # Set nullable integer values to 0
            nullables_int = ['in_reply_to_status_id', 'quoted_status_id']
            for i in nullables_int:
                if tweets_info[i] == None:
                    tweets_info[i] = 0  # Set nullable integer values to 0
                    
            # Set nullable boolean values to 0
            nullables = ['coordinates']
            for i in nullables:
                if tweets_info[i] == None:
                    tweets_info[i] = 'NULL'  # Set nullable values to 'NULL'

            # print(f"Preprocessor time taken: {time.time() - start_time}")
            
            return tweets_info  # Return the processed tweet information
            
    except Exception as e:
        logging.error(f"Error: {e}")  # Log the error
        return None  # Return None in case of an error