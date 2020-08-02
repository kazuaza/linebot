from flask import Flask, request, abort
import glob
import os

import matplotlib.pyplot as plt
import japanize_matplotlib
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


sozo_df = pd.read_csv('./sozo_answer_anony.csv')
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
        buttons_template = ButtonsTemplate(
            title='どの機能を使用しますか？', text='（下記ボタンを押してください）', actions=[
                MessageAction(label='①業界について',
                              text='＜興味のある業界の該当番号を打ってください＞\n\nA0：メーカー\nA1：サービス・インフラ\nA2：商社' \
                                   '\nA3：ソフトウェア\nA4：小売\nA5：広告・出版・マスコミ\nA6：金融\nA7：官公庁・公社・団体'),
                MessageAction(label='②就活ツールについて',
                              text='＜興味のある就活ツールの該当番号を打ってください＞\n\nB0：サイト\nB1：本\nB2：エージェント\nB3：イベント・セミナー'),
                MessageAction(label='③インターンについて',
                              text='＜興味のある項目の該当番号を打ってください＞\n\nC0：業界について\nC1：時期について\nC2：期間について'),
                MessageAction(label='④OBOG訪問について',
                              text='＜興味のある項目の該当番号を打ってください＞\n\nD0：人数について\nD1：連絡ツールについて')
            ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'B0':
        empty_list = []
        for site in ['マイナビ', 'リクナビ', 'unistyle', 'ONE CAREER', '就活ノート', 'Open Work',
                     'みんなの就職活動', '外資就活ドットコム', 'キャリタス就活', 'クリ博ナビ', '利用していない']:
            empty_list.append([site, sozo_df['サイト'].apply(lambda y: site in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['サイト名', '割合']).sort_values(by='割合', ascending=False)
        df['割合'] = df['割合'].astype(str).apply(lambda y: y + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)
        df.index.name = '順位'

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns, loc='center', bbox=[0, 0, 1, 1])
        plt.savefig('test.jpeg', dpi=1000)
        
        url = 'https://sozo-recommendation.herokuapp.com' + '/test.jpeg'
        app.logger.info("url=" + url)
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(url, url))


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)
