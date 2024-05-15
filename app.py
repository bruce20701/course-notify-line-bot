from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from model import Course, LinkedList, Weather
import threading
import json
import time
import datetime
import random
import pytz
import csv
import requests

app = Flask(__name__)

#line_bot的Token、Channel Secret
line_bot_api = LineBotApi('Z/DS32IDtAwQC8yBulBAZQL3enTL/pvKhW4JEnm+EiF222i3NHnw9aVIHyyASGu06QnV3Kqn5bpFSAkwthPcQPMJtDEc954zBfGihpbM1I9CpHbGu5974ZUf/AH08DgU1Gc1zVRBF8neDXg6Tu5ShAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7cc891755e07abe8a085326c9ecbccfb')

# 1A2B遊戲
ansNum = []
gameMod = False

# 初始化陣列
courses = list()

# 讀取課程資訊
with open('courseInfo.csv', mode='r', encoding="utf-8") as file:
   reader = csv.DictReader(file)
   for row in reader:
      courses.append(Course(row['name'], row['day'], row['startTime'], row['endTime'], row['location']))

# 檢查課程時間
def checkTime():
   global line_bot_api
   index = 0
   curTime = datetime.datetime.now().astimezone(pytz.timezone("Asia/Taipei"))
   courseTime = datetime.datetime.strptime(courses[index].startTime, "%H:%M")
   while( ((curTime.weekday() + 1) * 24 + curTime.hour) * 60 + curTime.minute > ((int(courses[index].day) * 24 + courseTime.hour) * 60) + courseTime.minute):
         index = (index + 1) % len(courses)
         courseTime = datetime.datetime.strptime(courses[index].startTime, "%H:%M")
   while True:
      # 取得當前的系統時間，並將系統時間轉換為 GMT+8 時區的時間
      curTime = datetime.datetime.now().astimezone(pytz.timezone("Asia/Taipei"))
      # 將課程startTime轉成時間
      courseTime = datetime.datetime.strptime(courses[index].startTime, "%H:%M")
      
      if(((curTime.weekday() + 1) == int(courses[index].day)) and ((courseTime.hour * 60 + courseTime.minute) - (curTime.hour * 60 + curTime.minute)) < 30):
         messagestr = f"{courses[index]}"
         line_bot_api.push_message('U1f1282dd809d2b9aa85e4b7c07492117', TextSendMessage(text=messagestr))
         index = (index + 1) % len(courses)
   
      # 系統休息10秒
      time.sleep(10)

# 查詢天氣
def checkWeather(locationName):
   url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"

   parameters = {
      'Authorization':"CWB-111EAC52-3B14-46FE-A793-4081D3E0576D",
      'locationName':locationName
   }

   response = requests.get(url, params=parameters)
   try:
      data = response.json()
      #取得特定城市的天氣(搜尋單一城市，所以只list內只有第0項)
      data = data['records']['location'][0]
      wx = data['weatherElement'][0]['time'][0]["parameter"]["parameterName"]
      pop = data['weatherElement'][1]['time'][0]["parameter"]["parameterName"]
      minT = data['weatherElement'][2]['time'][0]["parameter"]["parameterName"]
      ci = data['weatherElement'][3]['time'][0]["parameter"]["parameterName"]
      maxT = data['weatherElement'][4]['time'][0]["parameter"]["parameterName"]
      message = Weather(wx, maxT, minT, ci, pop)
      return f"{message}"
   except:
      return "查無資料，請確認是否輸入正確名稱"

# 1A2B遊戲
def playGame(msg):
   global ansNum, gameMod
   numList = []
   countA = 0
   countB = 0
   try:
      for i in range(len(msg)):
         numList.append(int(msg[i]))
      for i in range(max(len(msg), len(ansNum))):
         if numList[i] == ansNum[i]:
            countA += 1
         elif numList[i] in ansNum:
            countB += 1
      if countA == 4:
         message = f"恭喜答對，答案是{msg}\n要再次遊玩的話，請重新輸入「1A2B遊戲」"
         gameMod = False
      else:
         message = f"{countA}A{countB}B"
   except:
      message = "輸入格式有誤，請重新輸入"
   return message

# 初始化1A2B遊戲數字
def initGame():
   global ansNum
   # 產生4個0~9之間的數，數字不會重複
   ansNum = random.sample(range(10), 4)
   print(f"答案：{ansNum}")

# 接受使用者訊息
@app.route("/", methods=['POST'])
def linebot():
   global line_bot_api, handler, gameMod
   body = request.get_data(as_text=True)
   json_data = json.loads(body)
   try:
      signature = request.headers['X-Line-Signature']
      handler.handle(body, signature)
      # 讀取回應Token
      replyTk = json_data['events'][0]['replyToken']
      # 讀取使用者輸入內容
      userMsg = json_data['events'][0]['message']['text']
      if gameMod:
         if userMsg == "退出":
            gameMod = False
            message = "遊戲退出"
            line_bot_api.reply_message(replyTk, TextSendMessage(text=message))
         else:
            message = playGame(userMsg)
            line_bot_api.reply_message(replyTk, TextSendMessage(text=message))
      else:
         # 判斷使用者輸入內容
         if userMsg.startswith("查詢天氣"):
            message = checkWeather(userMsg[5:8])
            line_bot_api.reply_message(replyTk, TextSendMessage(text=message))
         elif userMsg == "1A2B遊戲":
            gameMod = True
            initGame()
            message = "1A2B遊戲開始\n請輸入4個數字\n如果要退出的話請輸入「退出」"
            line_bot_api.reply_message(replyTk, TextSendMessage(text=message))
         elif userMsg == "功能說明":
            message = "1. 查詢天氣:輸入「查詢天氣 縣市名」以獲取天氣狀況資訊。\n2. 1A2B遊戲:輸入「1A2B遊戲」已開始遊戲，遊戲期間可輸入「退出」可離開遊戲\n3. 課程提醒:機器人會在課程開始前30分鐘自動傳送訊息提醒上課"
            line_bot_api.reply_message(replyTk, TextSendMessage(text=message))
   except:
      print('error')
   return 'OK'

if __name__ == "__main__":
   # 定期偵測時間，每秒檢查一次
   check_thread = threading.Thread(target=checkTime)
   check_thread.start()

   # 啟動應用程式
   app_thread = threading.Thread(target=app.run)
   app_thread.start()