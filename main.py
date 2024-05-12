import re
import timeit
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
            initializer.drop(connection, 'conversation')
        elif choice == 'make':
            initializer.table(connection)
        elif choice == 'csvadd':
            loader.csv_adder(data, output_file='dataset.csv')
        elif choice == 'csvload':
            loader.tweets_loader_csv(connection, data, path='dataset.csv')
        elif choice == 'load':
            loader.tweets_loader(connection, data)  
        elif choice == 'conver':
            loader.conversation_loader(connection, data)
        elif choice == 'a':
            a = loader.csv_adder(data, output_file='dataset.csv')
            [next(a) for i in range(3)]
        else:
            print("Invalid choice.")

    connection.close()