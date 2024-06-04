import pandas as pd

file1 = pd.read_csv('tweets_dataset_khoi.csv')
file2 = pd.read_csv('tweets_dataset_ilse.csv')
file3 = pd.read_csv('tweets_dataset_illija.csv')
file4 = pd.read_csv('tweets_dataset_jan.csv')
file5 = pd.read_csv('tweets_dataset_oliver.csv')
file6 = pd.read_csv('tweets_dataset_sven.csv')
file7 = pd.read_csv('tweets_dataset_sven2.csv')

combined = pd.concat([file1, file2, file3, file4, file5, file6, file7])

combined.to_csv('combined_dataset.csv', index=False)

# cat tweets_dataset_khoi.csv <(tail -n +2 tweets_dataset_illija.csv) <(tail -n +2 tweets_dataset_sven.csv) > combined.csv