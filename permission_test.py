# create a folder and create an empty file in it

import os

from main import CURRENT_DIR

folder_path = os.path.join(CURRENT_DIR, 'test_folder')

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

file_path = os.path.join(folder_path, 'test_file.txt')

with open(file_path, 'w') as f:
    f.write('test')

with open(file_path, 'r') as f:
    print(f.read())

