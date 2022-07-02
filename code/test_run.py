import argparse
import textwrap
from test_class import *

def main():
    parser = argparse.ArgumentParser(
        description='test Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''実行例:
        # デフォルト起動(設問１がデフォルト)
        test_run.py
        # 設問ごとに出力を変更(以下設問1の場合)
        test_run.py -q 1
        # 設問2において、n回を指定する(デフォルト1回)
        test_run.py -q 2 -n 2
        # 設問3において、直近m回(デフォルト1回)、平均応答時間t秒(デフォルト10000秒)を指定する
        test_run.py -q 3 -m 2 -t 100
        '''))
     
    parser.add_argument('-q', '--question', type=int, default=1, help='設問番号')
    parser.add_argument('-n', '--number', type=int, default=1, help='連続タイムアウト回数')
    parser.add_argument('-t', '--time', type=int, default=10000, help='平均応答時間')
    parser.add_argument('-m', '--margin', type=int, default=1, help='直近m回')
    args = parser.parse_args()
     
    if args.question == 1:
        dtool = DetectTool_1(args=args)
        print(dtool.run())
    elif args.question == 2:
        dtool = DetectTool_2(args=args)
        print(dtool.run())
    elif args.question == 3:
        dtool = DetectTool_3(args=args)
        print(dtool.run())
    


if __name__ == '__main__':
     main()