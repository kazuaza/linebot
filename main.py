from flask import Flask, request, abort
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
# from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)


num = 0
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
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    
    if event.message.text == 'buttons':
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping'),
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', 
                              text=ButtonsTemplate(title='My buttons sample', text='Hello, my buttons', 
                                                   actions=[URIAction(label='Go to line.me', uri='https://line.me')])
                              )
                ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)


#     return text

# while True:
#     text = handle_message(MessageEvent)
#     if num == 0 and text == 'start':
#         text1 = '''
#         どの機能を利用しますか？
        
#         ①業界について
#         ②就活ツールについて
#         ③インターンについて
#         ④OB・OG訪問について
#         ⑤その他（感想等）
#         '''
#         num += 1
#         line_bot_api.reply_message(MessageEvent.reply_token, TextSendMessage(text=text1))
#         break
#     else:
#         text_exception = 'サービス利用の際は start と打ってください'
#         line_bot_api.reply_message(MessageEvent.reply_token, TextSendMessage(text=text_exception))
#         continue

if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)
