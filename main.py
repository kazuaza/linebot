from flask import Flask, request, abort
import os

import numpy as np
import pandas as pd
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
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
def handle_text_message(event):
    text = event.message.text

    if text == 'start':
        path = os.getcwd()
        buttons_template = ButtonsTemplate(
            title='どの機能を使用しますか？', text='（下記ボタンを押してください）', actions=[
                MessageAction(label='①業界について',
                              text='＜興味のある業界の該当番号を打ってください＞\n\n100：メーカー\n101：サービス・インフラ\n102：商社' \
                                   '\n103：ソフトウェア\n104：小売\n105：広告・出版・マスコミ\n106：金融\n107：官公庁・公社・団体'),
                MessageAction(label='②就活ツールについて',
                              text='＜興味のある就活ツールの該当番号を打ってください＞\n\n200：サイト\n201：本\n202：エージェント\n203：イベント・セミナー'),
                MessageAction(label='③インターンについて',
                              text='＜興味のある項目の該当番号を打ってください＞\n\n300：業界について\n301：時期について\n302：期間について'),
                MessageAction(label='④OBOG訪問について',
                              text=path)
            ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    # elif text == '200':


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)
