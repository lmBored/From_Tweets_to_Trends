import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from pathlib import Path

data = [Path("data/"+file) for file in os.listdir('data')]

with open('json_files.txt', 'w') as f:
    f.write('\n'.join(str(file).replace('data\\', '') for file in data))
print("Files written to json_files.txt.")