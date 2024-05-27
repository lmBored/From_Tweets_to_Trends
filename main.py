from preprocess import loader, initializer, conversation
import os
from pathlib import Path
import mysql.connector
from config import config

if __name__ == '__main__':
    data = [Path("data/"+file) for file in os.listdir('data')]

    connection = mysql.connector.connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'), allow_local_infile=True)    

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
            loader.tweets_loader_csv(connection, data)
        
        elif choice == 'csvloadusers':
            loader.users_loader_csv(connection, data)
            
        elif choice == 'clean_conver':
            conversation.conversation_clear(connection)
            
        elif choice == 'conver':
            conversation.conversation_adder(connection)
            
        elif choice == 'normalize':
            conversation.normalize(connection)
        
        elif choice == 'a':
            a = loader.csv_adder(data, output_file='dataset.csv')
            [next(a) for i in range(1)]
        else:
            print("Invalid choice.")

    connection.close()