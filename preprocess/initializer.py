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
    tweets_query = f"""
                CREATE TABLE `{config.get('DATABASE')}`.`tweets` 
                (`id` BIGINT ,
                `text` TEXT NULL ,
                `in_reply_to_status_id` BIGINT NULL , 
                `coordinates` TEXT NULL ,
                `timestamp_ms` BIGINT NULL ,
                `quoted_status_id` BIGINT NULL ,
                `user_id` BIGINT NULL ,
                `language` VARCHAR(5) NULL ,
                `mentioned_airlines` TEXT NULL ,
                `user_mentions` TEXT NULL ,
                `label` TEXT NULL ,
                `score` FLOAT NULL ,
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES `users`(user_id),
                FOREIGN KEY (retweeted_status_user_id) REFERENCES `users`(user_id)) ENGINE=InnoDB
                """
    users_query = f"""
                CREATE TABLE `{config.get('DATABASE')}`.`users`
                (`verified` BOOLEAN NOT NULL,
                `followers_count` INT NOT NULL,
                `statuses_count` INT NOT NULL,
                `user_id` BIGINT,
                PRIMARY KEY (user_id)) ENGINE=InnoDB
                """
    conversation_query = f"""
                CREATE TABLE `{config.get('DATABASE')}`.`conversations`
                (`conversation_id` BIGINT,
                `start` BIGINT NOT NULL,
                `end` BIGINT NOT NULL,
                `airline` VARCHAR(50) NOT NULL DEFAULT '0',
                `length` INT NOT NULL,
                PRIMARY KEY (conversation_id)) ENGINE=InnoDB
                """
    hasher_query = f"""
                CREATE TABLE `{config.get('DATABASE')}`.`hasher`
                (`id` BIGINT NOT NULL,
                `conversation_id` BIGINT NOT NULL,
                `conversation_rank` SMALLINT NOT NULL,
                PRIMARY KEY (id, conversation_id), 
                FOREIGN KEY (id) REFERENCES `tweets`(id),
                FOREIGN KEY (conversation_id) REFERENCES `conversations`(conversation_id)) ENGINE=InnoDB
                """
    connection.cursor().execute(users_query)
    connection.cursor().execute(tweets_query)
    connection.cursor().execute(conversation_query)
    connection.cursor().execute(hasher_query)
    print("✅ Tables created!")

def drop(connection, table):
    connection.cursor().execute(f"DROP TABLE IF EXISTS {table}")
    print("✅ Table dropped!")
    
def drop_all(connection):
    connection.cursor().execute("DROP DATABASE IF EXISTS "+config.get('DATABASE'))
    print("✅ Database dropped!")
    connection.cursor().execute("CREATE DATABASE "+config.get('DATABASE'))
    print("✅ Database created!")
    connection.cursor().execute("USE "+config.get('DATABASE'))
    print("✅ Database selected!")
    table(connection)
    
def delete(connection, table):
    connection.cursor().execute(f"DELETE FROM {table}")
    print("✅ Table deleted!")
