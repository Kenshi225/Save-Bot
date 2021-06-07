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

#�h���R�X�g���ϖ@��BTC�ςݗ��āB�o�b�`�t�@�C���Ȃǂŉ񂷃o�[�W����

#�J�n�����\��
print(datetime.now())

# �p�����[�^ #######################
VOL = 2740 #����BTC���w��������z�i�~�j
ZURE = 0 #�w�������������_���ł��炷�͈́B�P�ʂ͕b�B3600�łP����
exchange = "liquid" #�g�p�����������w��Bliquid, bitflyer, coincheck, bitbank�ȂǂɑΉ�
apikey = "" #�g�p����������API�L�[
secret = "" #�g�p����������secret�L�[
fname = "tmt.csv" #�ۑ�����csv�t�@�C����
###################################

#�ϐ�������#########################
ex = eval("ccxt."+exchange+"()")
ex.apiKey = apikey
ex.secret = secret
PAIR = "BTC/JPY"
limits = {"liquid": {"min":0.001, "rou":10000000},
         "coincheck":{"min":0.001, "rou":10000},
         "bitflyer":{"min":0.001, "rou":10000},
         "bitbank":{"min":0.0001, "rou":10000},}
STIME = 1 #�ҋ@����
###################################

#�c���𒲂ׂ�
try:
   balance1 = ex.fetch_balance()
except Exception as e:
   print(datetime.now())
   print(e)


#���g��������̎����������̂ő�����Ȃ���
balance1_btc = float(balance1['BTC']['total'])
balance1_jpy = float(balance1['JPY']['total'])

print(balance1_btc)
print(balance1_jpy)

#BTC���i�𒲂ׂ�Bticker���order_book������
book = ex.fetch_order_book(PAIR, 5)
print(book["asks"][0][0])
#BTC���i��f�ɍw����[BTC]�����肷��
amount = VOL / book["asks"][0][0]
print(amount)

amount = max((amount * limits[exchange]["rou"]//1)/limits[exchange]["rou"], limits[exchange]["min"])

print(amount)
#�w�����������炷�s��
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
       #�c���𒲂ׂ�
       balance2 = ex.fetch_balance()
       #���g��������̎����������̂ő�����Ȃ���
       balance2_btc = float(balance2['BTC']['total'])
       balance2_jpy = float(balance2['JPY']['total'])
       print(f"{balance2_btc}, {balance2_jpy}")
       if balance2_btc > balance1_btc and balance2_jpy < balance1_jpy:
           break

   # �O��̒l�擾
   csv_file = open("./" + fname, "r", encoding="ms932", errors="", newline="")
   f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"',
                  skipinitialspace=True)
   header = next(f)
   for row in f:
       last_row = row
   pre_btc = float(last_row[3])  # BTC���v
   pre_jpy = float(last_row[4])  # �����z���v
   # �L�^
   f = open(fname, 'a')
   writer = csv.writer(f, lineterminator='\n')
   writer.writerow([datetime.now(), #����
                    str(balance2_btc - balance1_btc), #�w����
                    str(balance1_jpy - balance2_jpy), #�w���z
                    str(pre_btc + balance2_btc - balance1_btc), #BTC���v
                    str(pre_jpy + balance1_jpy - balance2_jpy), #�����z���v
                    str(book["bids"][0][0] * (pre_btc + balance2_btc - balance1_btc)) #���݉��l
                    ])
   f.close()