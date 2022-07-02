import pandas as pd

def read_log():
    filename = './logs/sample_log.txt'
    df = pd.read_csv(filename, 
                     header=None, 
                     names=['date', 'addr', 'result'], )
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d%H%M%S')

    return df