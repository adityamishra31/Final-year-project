import re

# for validating an Email 
def validate_email(email):  
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):  
        return True 
    return False


import numpy as np
import csv

def convert_csv_to_dat(csv_file, dat_file):
    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(csv_file)
        data  = np.array(list(csv_reader))

    with open(dat_file, 'w') as f:
        data.tofile(f)

if __name__ == '__main__':
    csv_file = r'D:\final-year-project\datasets\Groceries data.csv'
    dat_file = 'data.dat'
    convert_csv_to_dat(csv_file, dat_file)

    