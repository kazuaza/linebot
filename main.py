from flask import Flask, request, abort
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, 
    ButtonsTemplate, MessageAction)


app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == 'start':
        buttons_template = ButtonsTemplate(
            title='どの機能を使用しますか？', text='（下記ボタンを押してください）', actions=[
                MessageAction(label='①業界について', text='test'),
                MessageAction(label='②就活ツールについて', text='test'),
                MessageAction(label='③インターンについて', text='test'),
                MessageAction(label='④OBOG訪問について', text='test'),
                MessageAction(label='⑤その他', text='test')
            ])
        template_message = TemplateSendMessage(template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)
