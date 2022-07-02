import datetime
from read_log import read_log
import pandas as pd

#設問1
class DetectTool_1:
    def __init__(self, args):
        self.term = 10 # ログ収集の間隔
        self.df = read_log() # ログ
        self.args = args
        self.unique_addr = pd.unique(self.df['addr']) # IP一覧
        
    def find_failure(self):
        if len(self.df.index) == 0:
            return 'No log Data'
        
        #結果格納スペース
        head = ['start', 'period(m)' , 'addr']
        failure_df = pd.DataFrame(index=[], columns=head)
        
        for addr in list(self.unique_addr):
            #IPアドレスごとに集計
            tmp = self.df.loc[self.df['addr'] == addr]
            print(tmp)
            
            # 初期値設定（時刻は仮に1500年として設定）
            count = 0
            start_date = datetime.datetime(1500, 1, 1)
            
            # 故障判定し、リストに投入
            for row in tmp.itertuples():
                if row.result == '-' and count == 0:
                    start_date = row.date
                    count += 1
                elif row.result == '-' :
                    count += 1
                elif row.result != '-' and count > 0:
                    record = pd.Series([start_date, self.term*count, addr], index=failure_df.columns)
                    failure_df = failure_df.append(record, ignore_index=True)
                    count = 0
                else:
                    pass
            
        if len(failure_df.index) == 0:
            return 'No failures have occurred'
        return failure_df
            
    def run(self):
        return self.find_failure()
    
#設問２   
class DetectTool_2(DetectTool_1):
    #オーバーライド
    def run(self):
        tmp = self.find_failure()
        
        #N回判定追加
        if type(tmp) != type('string'):
            tmp = tmp.loc[tmp['period(m)'] >= self.term*self.args.number]
            if len(tmp) == 0:
                return 'No failures have occurred'
            return tmp
        else:
            return tmp

#設問３
class DetectTool_3(DetectTool_2):
        
        
            
        
    