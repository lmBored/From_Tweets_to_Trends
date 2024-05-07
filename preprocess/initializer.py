from config import config

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

def table(connection):
    tweet_query = f"""
            CREATE TABLE `{config.get('DATABASE')}`.`tweets` 
            (`id` BIGINT ,
            `text` TEXT NULL ,
            `in_reply_to_status_id` BIGINT NULL , 
            `in_reply_to_user_id` BIGINT NULL ,
            `coordinates` TEXT NULL ,
            `reply_count` BIGINT NULL ,
            `retweet_count` INT NULL ,
            `favorite_count` BIGINT NULL ,
            `timestamp_ms` BIGINT NULL ,
            `verified` BOOLEAN NULL ,
            `followers_count` INT NULL ,
            `statuses_count` INT NULL ,
            `user_id` BIGINT NULL ,
            `language` VARCHAR(3) NULL ,
            `mentioned_airlines` TEXT NULL ,
            `user_mentions` TEXT NULL ,
            `retweeted_status` TEXT NULL ,
            PRIMARY KEY (id)) ENGINE=InnoDB
            """
    conversation_query = f"""
            CREATE TABLE `{config.get('DATABASE')}`.`conversation`
            (`id` BIGINT NULL ,
            'in_reply_to_status_id' BIGINT NULL ,
            `in_reply_to_user_id' BIGINT NULL ,
            PRIMARY KEY (id)) ENGINE=InnoDB
            """
    connection.cursor().execute(tweet_query)
    connection.cursor().execute(conversation_query)

def drop(connection, table):
    connection.cursor().execute(f"DROP TABLE IF EXISTS {table}")
