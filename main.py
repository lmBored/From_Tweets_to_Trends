from preprocess import preprocessor, loader, initializer

if __name__ = '__main__':
    data = [Path("data/"+file) for file in os.listdir('data')]

    connection = mysql.connector.connect(host=config.get('HOST'), user=config.get('USERNAME'), password=config.get('PASSWORD'),database=config.get('DATABASE'))
    
    initializer.table(connection)
    loader.csv_adder(data)
    loader.tweets_loader_csv(connection, data, path = 'dataset.csv')
    
    # or you can run this (not suggested)
    # loader.tweets_loader((connection, data)

    
