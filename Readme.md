# 実行方法
まずDocker(docker-compose含む)が入っている環境を用意する。<br/>
本Gitのリポジトリをクローンし、`docker-compose.yml`ファイルがある環境で以下を実行。
```
#dockerで環境立ち上げ
docker-compose up -d

#dockerで立ち上げたコンテナへ入る。
docker-compose exec test /bin/bash

#ツール実行
python test_run.py -q [設問番号] 
```
<br/>

# 各設問におけるツールの引数設定
詳細は以下のコマンドを実行し、確認してほしい。
```
python test_run.py -h
```

以下、簡単に引数の種類を説明する。<br/>
※すべて自然数を引数として欲しい。`invalid error`が発生するので。
```
 -q: 設問番号
 -n: N回の自然数指定(設問２で使用)
 -t: 平均応答時間指定(設問３で使用)
 -m: 直近m回の指定(設問３で使用)
```
<br/>

# テストについて
## テストデータ
以下階層に格納
```
code/logs/sample_log.txt
```
## 結果
### 設問１
```
root@e9f28b89e3c9:/code# python test_run.py -q 1
        failure_start period_minutes            addr
0 2020-10-19 13:33:24              1   10.20.30.1/16
1 2020-10-19 13:38:24              3   10.20.30.1/16
2 2020-10-19 13:38:25              3   10.20.30.2/16
3 2020-10-19 13:36:35              2  192.168.1.2/24
```
`failure_start`が故障発生時間、`period_minutes`が発生期間（分）、`addr`が発生箇所（IP）である。

### 設問２
```
root@e9f28b89e3c9:/code# python test_run.py -q 2 -n 2
        failure_start period_minutes            addr
1 2020-10-19 13:38:24              3   10.20.30.1/16
2 2020-10-19 13:38:25              3   10.20.30.2/16
3 2020-10-19 13:36:35              2  192.168.1.2/24
```
N回を2と設定した結果である。

### 設問３
```
root@e9f28b89e3c9:/code# python test_run.py -q 3 -t 500 -m 3
          failure_start period_minutes            addr
0   2020-10-19 13:34:24              8   10.20.30.1/16
5   2020-10-19 13:38:25              4   10.20.30.2/16
16  2020-10-19 13:36:35              5  192.168.1.2/24
```
平均応答時間指定を500ms、直近m回を3とした結果である。

### 設問４
```
root@e9f28b89e3c9:/code# python test_run.py -q 4
        failure_start period_minutes            addr SW_failure
0 2020-10-19 13:38:24              3    10.20.0.0/16       True
1 2020-10-19 13:33:24              1   10.20.30.1/16      False
2 2020-10-19 13:36:35              2  192.168.1.2/24      False
```
`addr`に関してはネットワークアドレスが追加されている。<br/>
`SW_failure`がスイッチの故障かどうかの判定結果で、この値が`True`の場合は`addr`がネットワークアドレスとなる。
<br/>

# コードについて
以下ディレクトリ階層

```
(カレント)
│- docker-compose.yml
│- Readme.md
│
├─code
│  │- read_log.py
│  │- test_class.py
│  │- test_run.py
│  │
│  └─logs
│        - sample_log.txt
│
└─docker_env
      - Dockerfile
      - requirements.txt
```

`code`ディレクトリ配下をコンテナ環境ｈへマウントしているので、基本的にこのディレクトリ配下のPythonコードを実行するようになっている。<br/>
※詳しいコードの説明は各Pythonファイル内部に記載している。<br/>
`docker_env`ディレクトリ配下は実行環境を整えるための各種設定のファイルを用意している。<br/>
`docker-compose.yml`ファイルは`docker-compose`コマンドを実行するための設定である。

## Pythonファイルについて
### read_log.py
`sample_log.txt`を`pandas`を使って`DataFrame`形式に読み込むためのコードを記載している。
### test_run.py
実際に実行するファイルである。`argparse.ArgumentParser`を使ってツールの引数を設定するためのメインファイル。
### test_class.py
各設問の集計出力ロジックを設計しているクラスファイルである。