from flask import Flask, request, abort
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, MessageAction)


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
            title='どの機能を利用しますか？', actions=[
                MessageAction(label='①業界について',
                              text='''
                              メーカー
                              サービス・インフラ
                              商社
                              ソフトウェア
                              小売
                              広告・出版・マスコミ
                              金融
                              官公庁・公社・団体
                              '''),
                MessageAction(label='②就活ツールについて',
                              text='test'),
                MessageAction(label='③インターンについて',
                              text='test'),
                MessageAction(label='④OB・OG訪問について',
                              text='test'),
                MessageAction(label='⑤その他（感想等）',
                              text='test')
            ])
        template_message = TemplateSendMessage(template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
        
    elif text == 'carousel':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
        
    else:
        pass


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)
