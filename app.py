from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import sys
import os

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('Yz/a0h8RwPd4UVcKCh2JtZ3YS14oOGig98HfFu9bMbmUkTdLCeMUAaYHAHyl3khJyLNl7aCpKWCK7yo4Q4tMn4oKGhQmoUhilm7s2wO38s7GlV8bGccZWT1c95zfAe0a9lNhluK3opvEqZ1R/4Gx6gdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('8993ebca810a9e844ec90d17f13d0c92')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        groupID = event.source.group_id
    except:
        message = TextSendMessage(text='我只接收群組內訊息，請先把我邀請到群組!')
        line_bot_api.reply_message(event.reply_token, message)
    else:
        if not reportData.get(groupID):
            reportData[groupID]={}
        LineMessage = ''
        receivedmsg = event.message.text
        if '姓名' in receivedmsg and '餐點' in receivedmsg :
            try:
                if ( len(receivedmsg.split('姓名')[-1].split('餐點')[0])<3):
                    raise Exception
                name = receivedmsg.split('姓名')[-1].split('餐點')[0][1:]
                # name = str(name)
            except Exception:
                LineMessage = '姓名、餐點，其中一項未填。'
            else:
                reportData[groupID][name] = receivedmsg
                name = str(name)
                LineMessage = str(name)+'回報成功。'

        elif '使用說明' in receivedmsg and len(receivedmsg)==4:
            LineMessage = (
                '收到以下正確格式\n'
                '才會正確記錄回報。\n'
                '----------\n'
                '姓名：\n'
                '餐點：\n'
                '----------\n'
                '\n'
                '指令\n'
                '----------\n'
                '•格式\n'
                '->格式範例。\n'
                '•統計\n'
                '->顯示完成回報的人員。\n'
                '•輸出\n'
                '->輸出所有回覆，並清空回報紀錄。\n'
                '•清空\n'
                '->可手動清空Data，除錯用。\n'
                '----------\n'
            )
        elif '統計' in receivedmsg and len(receivedmsg)==4:
            try:
                LineMessage = '目前完成回報的有：\n'
                i = 1
                for name in reportData[groupID]:
                    LineMessage = LineMessage + str(i) + '. '+name
                    i += 1
            except BaseException as err:
                LineMessage = '錯誤原因: '+str(err)

        elif '輸出' in receivedmsg and len(receivedmsg)==4:
            try:
                LineMessage = ''
                for data in [reportData[groupID][name] for name in sorted(reportData[groupID].keys())]:
                    LineMessage = LineMessage + data +'\n\n'
            except BaseException as err:
                LineMessage = '錯誤原因: '+str(err)
            else:
                reportData[groupID].clear()

        elif '格式' in receivedmsg and len(receivedmsg)==2:
            LineMessage = '姓名：\n餐點：\n'

        elif '清空' in receivedmsg and len(receivedmsg)==2:
            reportData[groupID].clear()
            LineMessage = '資料已重置!'

        if LineMessage :
            message = TextSendMessage(text=LineMessage)
            line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    global reportData
    reportData = {}
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)