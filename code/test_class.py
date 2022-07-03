import datetime
import pandas as pd
import ipaddress

from read_log import read_log

#設問1
class DetectTool_1:
    def __init__(self, args):
        self.term = 1 # ログ収集の間隔
        self.df = read_log() # ログ
        self.args = args
        self.unique_addr = pd.unique(self.df['addr']) # IP一覧
        
        #IPからネットワークアドレスを算出するlambda関数作成
        f_ipnet = lambda x: str(ipaddress.IPv4Interface(x).network)
        #ネットワークアドレスを新'network'カラムで格納
        self.df['network'] = self.df['addr'].apply(f_ipnet)
        
        self.unique_net = pd.unique(self.df['network']) # NetWork一覧
        
    def find_failure(self):
        if len(self.df.index) == 0:
            return 'No log Data'
        
        #結果格納スペース
        head = ['failure_start', 'period_minutes' , 'addr']
        failure_df = pd.DataFrame(index=[], columns=head)
        
        for addr in list(self.unique_addr):
            #IPアドレスごとに集計
            tmp = self.df.loc[self.df['addr'] == addr].sort_values('date')
            
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
            # 上記場合だとタイムアウト状態でログが終了していた場合に判定出来ないので、
            # タイムアウトが続いていた段階でリスト投入を行う
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
            tmp = tmp.loc[tmp['period_minutes'] >= self.term*self.args.number]
            if len(tmp) == 0:
                return 'No failures have occurred'
            return tmp
        else:
            return tmp


#設問３
class DetectTool_3(DetectTool_2):
    #オーバーライド
    def find_failure(self):
        if len(self.df.index) == 0:
            return 'No log Data'
        
        head = ['failure_start', 'period_minutes' , 'addr']
        failure_df = pd.DataFrame(index=[], columns=head)
        
        # '-'のタイムアウトに関しては10000msと仮定し、変換を行う
        self.df.loc[self.df['result'] == '-', 'result'] = '10000'
        self.df = self.df.astype({'result':'int64'})
        
        for addr in list(self.unique_addr):
            tmp = self.df.loc[self.df['addr'] == addr].sort_values('date')
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
    
    
#設問４
class DetectTool_4(DetectTool_2):
    #オーバーライド
    def find_failure(self):
        if len(self.df.index) == 0:
            return 'No log Data'
        
        head = ['failure_start', 'period_minutes' , 'addr', 'SW_failure']
        failure_df = pd.DataFrame(index=[], columns=head)
        
        #スイッチ故障判定
        for net in list(self.unique_net):
            #ネットワークアドレスごとに集計
            tmp = self.df.loc[self.df['network'] == net].sort_values('date')
            #初期値
            count = 0
            uniq_addr = pd.unique(tmp['addr']) #同プレフィックス内IPのユニークリスト
            flag_set = {ip: False for ip in uniq_addr} #同プレフィックス内IPでのタイムアウト有無フラグ
            start_date = datetime.datetime(1500, 1, 1)
            # スイッチが故障した時間帯は同分内でのタイムアウトが発生した場合とする。
            calc_date = tmp.iloc[0,0] #同時間帯判定用の変数初期値
            for row in tmp.itertuples():
                if row.date - calc_date < datetime.timedelta(minutes=1):
                    if row.result == '-' and not any(flag_set.values()) and count == 0:
                        start_date = row.date
                        flag_set[row.addr] = True
                    elif row.result == '-' and any(flag_set.values()):
                        flag_set[row.addr] = True
                    elif row.result != '-' and count > 0:
                        record = pd.Series([start_date, self.term*count, net, True], index=failure_df.columns)
                        failure_df = failure_df.append(record, ignore_index=True)
                        flag_set = {ip: False for ip in uniq_addr}
                        count = 0
                    else:
                      pass
                else:
                    calc_date = row.date
                    if row.result == '-' and all(flag_set.values()):
                        count += 1
                        flag_set = {ip: False for ip in uniq_addr}
                        flag_set[row.addr] = True
                    elif row.result != '-' and all(flag_set.values()):
                        count += 1
                        record = pd.Series([start_date, self.term*count, net, True], index=failure_df.columns)
                        failure_df = failure_df.append(record, ignore_index=True)
                        flag_set = {ip: False for ip in uniq_addr}
                        count = 0
                    elif row.result == '-' and not any(flag_set.values()) and count == 0:
                        start_date = row.date
                        flag_set[row.addr] = True
                    elif row.result != '-' and any(flag_set.values()):
                        flag_set = {ip: False for ip in uniq_addr}
                        
            if all(flag_set.values()):
                count += 1
                record = pd.Series([start_date, self.term*count, net, True], index=failure_df.columns)
                failure_df = failure_df.append(record, ignore_index=True)
                
        switch_fail_list = failure_df
            
        #通常故障
        for addr in list(self.unique_addr):
            tmp = self.df.loc[self.df['addr'] == addr].sort_values('date')
            count = 0
            start_date = datetime.datetime(1500, 1, 1)
            
            #スイッチ故障時の時間帯を除外
            for swfail in switch_fail_list.itertuples():
                del_date_end = swfail.failure_start + datetime.timedelta(minutes=swfail.period_minutes)
                tmp = tmp.drop(index = tmp.loc[(tmp['date'] < del_date_end) & (tmp['date'] >= swfail.failure_start)].index)
                
            # 故障判定
            for row in tmp.itertuples():
                if row.result == '-' and count == 0:
                    start_date = row.date
                    count += 1
                elif row.result == '-' :
                    count += 1
                elif row.result != '-' and count > 0:
                    record = pd.Series([start_date, self.term*count, addr, False], index=failure_df.columns)
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
        
    