from preprocess import loader, initializer, preprocessor
import os
from pathlib import Path
import mysql.connector
from config import config

if __name__ == '__main__':
    data = [Path("data/"+file) for file in os.listdir('data')]

    connection = mysql.connector.connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'), allow_local_infile=True)    

    initializer.drop(connection, 'tweets')
    initializer.drop(connection, 'conversation')
    initializer.table(connection)
    # loader.csv_adder(data)
    # loader.tweets_loader_csv(connection, data, path = 'dataset.csv')
    
    # or you can run this
    loader.tweets_loader((connection, data)

    
