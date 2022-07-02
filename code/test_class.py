import datetime
from read_log import read_log
import pandas as pd

#設問1
class DetectTool_1:
    def __init__(self, args):
        self.term = 1 # ログ収集の間隔
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
                
            if count > 0:
                record = pd.Series([start_date, self.term*count, addr], index=failure_df.columns)
                failure_df = failure_df.append(record, ignore_index=True)
            
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
    def find_failure(self):
        if len(self.df.index) == 0:
            return 'No log Data'
        
        head = ['start', 'period(m)' , 'addr']
        failure_df = pd.DataFrame(index=[], columns=head)
        
        # '-'のタイムアウトに関してはタイムアウト10000msと仮定し、変換を行う
        self.df['result'].loc[self.df['result'] == '-'] = '10000'
        self.df = self.df.astype({'result':'int64'})
        
        for addr in list(self.unique_addr):
            tmp = self.df.loc[self.df['addr'] == addr]
            # print(tmp)
            count = 0
            start_date = datetime.datetime(1500, 1, 1)
            
            for row in tmp.itertuples():
                before_log_date = row.date - datetime.timedelta(minutes=self.term*self.args.margin)
                # 直近m回の過去ログが取ることが可能な場合に判定を実施
                if tmp.iloc[0,0] <= before_log_date:
                    # 該当時間以前のm回のログで平均を計算
                    mean = tmp['result'].loc[(tmp['date'] >= before_log_date) & (tmp['date'] <= row.date)].mean()
                    
                    if mean > self.args.time and count == 0:
                        start_date = row.date
                        count += 1 
                    elif mean > self.args.time:
                        count += 1 
                    elif mean < self.args.time:
                        record = pd.Series([start_date, self.term*count, addr], index=failure_df.columns)
                        failure_df = failure_df.append(record, ignore_index=True)
                        count = 0
                    else:
                        pass
                else:
                    pass
                
            if count > 0:
                record = pd.Series([start_date, self.term*count, addr], index=failure_df.columns)
                failure_df = failure_df.append(record, ignore_index=True)
                
            
        if len(failure_df.index) == 0:
            return 'High load conditions have not occurred (or be too few logs)'
        return failure_df
        
    