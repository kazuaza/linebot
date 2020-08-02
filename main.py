from flask import Flask, request, abort
import glob
import time
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
        time.sleep(2)

    elif text == 'B0':
        empty_list = []
        for site in ['マイナビ', 'リクナビ', 'unistyle', 'ONE CAREER', '就活ノート', 'Open Work',
                     'みんなの就職活動', '外資就活ドットコム', 'キャリタス就活', 'クリ博ナビ', '利用していない']:
            empty_list.append([site, sozo_df['サイト'].apply(lambda y: site in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜サイト名＞', '＜割合＞']).sort_values(by='割合', ascending=False)
        df['割合'] = df['割合'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 利用就活サイト一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b0.png', dpi=300)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_b0.png'

        others = np.setdiff1d(sozo_df['サイト'].apply(lambda y: y.split(';')[-1]).values,
                              ['マイナビ', 'リクナビ', 'unistyle', 'ONE CAREER', '就活ノート', 'Open Work',
                               'みんなの就職活動', '外資就活ドットコム', 'キャリタス就活', 'クリ博ナビ', '利用していない'])
        send_text = '＜その他＞\n'
        for i in range(len(others)):
            if i == len(others)-1:
                send_text += '・{}'.format(others[i])
            else:
                send_text += '・{}\n'.format(others[i])

        line_bot_api.reply_message(event.reply_token,
                                   [ImageSendMessage(url, url), TextSendMessage(text=send_text)])
        time.sleep(2)

    elif text == 'B1':
        empty_list = []
        for book in ['絶対内定2021シリーズ', '就職活動が面白いほどうまくいく確実内定', '四季報', '最新！SPI3',
                     '史上最強SPI&テストセンター', '利用していない']:
            empty_list.append([book, sozo_df['本'].apply(lambda y: book in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜書籍名＞', '＜割合＞']).sort_values(by='割合', ascending=False)
        df['割合'] = df['割合'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 利用就活本一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b1.png', dpi=300)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_b1.png'

        others = np.setdiff1d(sozo_df['本'].apply(lambda y: y.split(';')[-1]).values,
                              ['絶対内定2021シリーズ', '就職活動が面白いほどうまくいく確実内定', '四季報', '最新！SPI3',
                               '史上最強SPI&テストセンター', '利用していない'])
        send_text = '＜その他＞\n'
        for i in range(len(others)):
            if i == len(others)-1:
                send_text += '・{}'.format(others[i])
            else:
                send_text += '・{}\n'.format(others[i])

        line_bot_api.reply_message(event.reply_token,
                                   [ImageSendMessage(url, url), TextSendMessage(text=send_text)])
        time.sleep(2)

    elif text == 'B2':
        empty_list = []
        for agent in ['大学のキャリアセンター', 'マイナビ新卒紹介', 'リクナビ就職エージェント',
                      'キャリアチケット', '利用していない']:
            empty_list.append([agent, sozo_df['エージェント'].apply(lambda y: agent in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜エージェント名＞', '＜割合＞']).sort_values(by='割合', ascending=False)
        df['割合'] = df['割合'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 利用エージェント一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b2.png', dpi=300)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_b2.png'

        others = np.setdiff1d(sozo_df['エージェント'].apply(lambda y: y.split(';')[-1]).values,
                              ['大学のキャリアセンター', 'マイナビ新卒紹介', 'リクナビ就職エージェント',
                               'キャリアチケット', '利用していない'])
        send_text = '＜その他＞\n'
        for i in range(len(others)):
            if i == len(others)-1:
                send_text += '・{}'.format(others[i])
            else:
                send_text += '・{}\n'.format(others[i])

        line_bot_api.reply_message(event.reply_token,
                                   [ImageSendMessage(url, url), TextSendMessage(text=send_text)])
        time.sleep(2)

    elif text == 'B3':
        empty_list = []
        for event in ['学内イベント', 'マイナビ就職EXPO', 'リクナビイベント', 'MeetsCompany', 'キャリアチケットラボ',
                      '就職エージェントneo', 'ジョブコミット', '利用していない']:
            empty_list.append([event, sozo_df['イベント・セミナー'].apply(lambda y: event in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['イベント・セミナー名', '割合']).sort_values(by='割合', ascending=False)
        df['割合'] = df['割合'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 利用イベント・セミナー一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b3.png', dpi=300)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_b3.png'

        others = np.setdiff1d(sozo_df['イベント・セミナー'].apply(lambda y: y.split(';')[-1]).values,
                              ['学内イベント', 'マイナビ就職EXPO', 'リクナビイベント', 'MeetsCompany', 'キャリアチケットラボ',
                               '就職エージェントneo', 'ジョブコミット', '利用していない'])
        send_text = '＜その他＞\n'
        for i in range(len(others)):
            if i == len(others) - 1:
                send_text += '・{}'.format(others[i])
            else:
                send_text += '・{}\n'.format(others[i])

        line_bot_api.reply_message(event.reply_token,
                                   [ImageSendMessage(url, url), TextSendMessage(text=send_text)])
        time.sleep(2)


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)
