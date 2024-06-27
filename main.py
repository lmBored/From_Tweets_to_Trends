import os
# os.makedirs('tmp', exist_ok=True)
if not os.path.exists('tmp'): # create a tmp directory if it hasn't been created
    os.makedirs('tmp')
    print("✅ Created tmp directory.")
from preprocess import loader, initializer, conversation
from sentiment import categorize
from pathlib import Path
import mysql.connector
from mysql.connector import connect
from config import config

if __name__ == '__main__':
        
    data = [Path("data/"+file) for file in os.listdir('data')]
    data.sort(key=lambda x: x.name)

    connection = mysql.connector.connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'), allow_local_infile=True)  
    # with connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'), allow_local_infile=True) as connection:
    
    while True:
        choice = input("Which? ")
        if choice == 'q':
            break
        elif choice == 'drop':
            initializer.drop(connection, 'tweets')
            initializer.drop(connection, 'users')
            initializer.drop(connection, 'hasher')
            initializer.drop(connection, 'conversations')
            
        elif choice == 'dropall': # Drop all tables and recreate them
            initializer.drop_all(connection)
            
        elif choice == 'make':
            initializer.table(connection)
            
        elif choice == 'delete':
            initializer.delete(connection, 'tweets')
            initializer.delete(connection, 'users')
            initializer.delete(connection, 'hasher')
            initializer.delete(connection, 'conversations')
            
        elif choice == 'csvaddtweets':
            loader.csv_adder_tweets(data)
        
        elif choice == 'csvadduser':
            loader.csv_adder_users(data)
            
        # LOAD DATA LOCAL INFILE '~/dbl_data_challenge/tweets_dataset.csv' INTO TABLE tweets FIELDS TERMINATED BY ',' ENCLOSED BY "'"  IGNORE 1 ROWS;
        elif choice == 'csvloadtweets':
            loader.tweets_loader_csv(connection)
        
        elif choice == 'csvloadusers':
            loader.users_loader_csv(connection)
            
        elif choice == 'clean_conver':
            conversation.conversation_clear(connection)
            
        elif choice == 'conver':
            conversation.conversation_adder(connection)
            
        elif choice == 'normalize':
            conversation.normalize(connection)
        
        elif choice == 'add_rank_col':
            connection.cursor().execute('ALTER TABLE `hasher` ADD COLUMN `conversation_rank` SMALLINT NOT NULL')
            connection.commit()
        
        elif choice == 'a':
            a = loader.csv_adder_tweets(data, output_file='dataset.csv')
            [next(a) for i in range(1)]
            
        elif choice == 'setup': # Run this to setup everything from beginning to conversation
            initializer.drop_all(connection)
            loader.tweets_loader_csv(connection)
            loader.users_loader_csv(connection)
            conversation.conversation_adder(connection)
            conversation.normalize(connection)
            
        elif choice == "setup_conversation": # Run this to add data to conversation and hasher tables only
            conversation.conversation_clear(connection)
            conversation.conversation_adder(connection)
            conversation.normalize(connection)
            
        elif choice == 'conversation_and_hasher_to_csv': # Convert conversation and hasher tables to csv
            conversation.convert_conversations_table_to_csv(connection)
            conversation.convert_hasher_table_to_csv(connection)
            
        elif choice == 'csvloadconversationshasher': # Load conversation and hasher tables from csv
            conversation.csv_loader_hasher(connection)
            conversation.csv_loader_conversations(connection)
        
        elif choice == 'categorize': # Categorize tweets into topics
            categorize.drop(connection)
            categorize.categorize(connection)
            
        elif choice == 'fck_the_tweets':
            cursor = connection.cursor()
    
            # Delete corresponding rows in hasher table
            query = "DELETE FROM hasher WHERE id IN (SELECT id FROM tweets WHERE user_id = 0)"
            cursor.execute(query)
            
            # Delete tweets
            query = "DELETE FROM tweets WHERE user_id = 0"
            cursor.execute(query)
            
            connection.commit()
        
        else:
            print("Invalid choice.")

    if connection.is_connected():
        connection.close()