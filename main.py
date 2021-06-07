# -*- coding: utf-8 -*-
import ccxt
import time
import threading
from pprint import pprint
from datetime import datetime
from threading import Thread
import csv
import requests
from pathlib import Path
import random

#ドルコスト平均法でBTC積み立て。バッチファイルなどで回すバージョン

#開始時刻表示
print(datetime.now())

# パラメータ #######################
VOL = 2740 #毎日BTCを購入する金額（円）
ZURE = 0 #購入時刻をランダムでずらす範囲。単位は秒。3600で１時間
exchange = "liquid" #使用する取引所を指定。liquid, bitflyer, coincheck, bitbankなどに対応
apikey = "" #使用する取引所のAPIキー
secret = "" #使用する取引所のsecretキー
fname = "tmt.csv" #保存するcsvファイル名
###################################

#変数初期化#########################
ex = eval("ccxt."+exchange+"()")
ex.apiKey = apikey
ex.secret = secret
PAIR = "BTC/JPY"
limits = {"liquid": {"min":0.001, "rou":10000000},
         "coincheck":{"min":0.001, "rou":10000},
         "bitflyer":{"min":0.001, "rou":10000},
         "bitbank":{"min":0.0001, "rou":10000},}
STIME = 1 #待機時間
###################################

#残高を調べる
try:
   balance1 = ex.fetch_balance()
except Exception as e:
   print(datetime.now())
   print(e)


#中身が文字列の取引所があるので代入しなおす
balance1_btc = float(balance1['BTC']['total'])
balance1_jpy = float(balance1['JPY']['total'])

print(balance1_btc)
print(balance1_jpy)

#BTC価格を調べる。tickerよりorder_bookが無難
book = ex.fetch_order_book(PAIR, 5)
print(book["asks"][0][0])
#BTC価格を素に購入量[BTC]を決定する
amount = VOL / book["asks"][0][0]
print(amount)

amount = max((amount * limits[exchange]["rou"]//1)/limits[exchange]["rou"], limits[exchange]["min"])

print(amount)
#購入時刻をずらす行為
time.sleep(ZURE * random.random())

try:
   order = ex.create_market_buy_order(PAIR, amount)
except Exception as e:
   print(datetime.now())
   print(e)
else:
   print(order)
   while True:
       time.sleep(STIME)
       #残高を調べる
       balance2 = ex.fetch_balance()
       #中身が文字列の取引所があるので代入しなおす
       balance2_btc = float(balance2['BTC']['total'])
       balance2_jpy = float(balance2['JPY']['total'])
       print(f"{balance2_btc}, {balance2_jpy}")
       if balance2_btc > balance1_btc and balance2_jpy < balance1_jpy:
           break

   # 前回の値取得
   csv_file = open("./" + fname, "r", encoding="ms932", errors="", newline="")
   f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"',
                  skipinitialspace=True)
   header = next(f)
   for row in f:
       last_row = row
   pre_btc = float(last_row[3])  # BTC合計
   pre_jpy = float(last_row[4])  # 投資額合計
   # 記録
   f = open(fname, 'a')
   writer = csv.writer(f, lineterminator='\n')
   writer.writerow([datetime.now(), #時刻
                    str(balance2_btc - balance1_btc), #購入量
                    str(balance1_jpy - balance2_jpy), #購入額
                    str(pre_btc + balance2_btc - balance1_btc), #BTC合計
                    str(pre_jpy + balance1_jpy - balance2_jpy), #投資額合計
                    str(book["bids"][0][0] * (pre_btc + balance2_btc - balance1_btc)) #現在価値
                    ])
   f.close()