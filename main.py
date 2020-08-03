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
sozo_df_permit = sozo_df[sozo_df['興味をもった後輩に名前を教えて良いですか？'] == '良い']

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

    elif text == 'A0':
        empty_list = []
        maker_list = ['食品・農林・水産', '建設・住宅・インテリア', '繊維・化学・薬品・化粧品', '鉄鋼・金属・鉱業',
                      '機械・プラント', '電子・電気機器', '自動車・輸送用機器', '精密・医療用機器',
                      '印刷・事務機器関連', 'スポーツ・玩具・ゲーム']
        for maker in maker_list:
            true_index = sozo_df_permit['メーカー'].apply(lambda y: maker in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['メーカー'].apply(lambda y: y.split(';')[-1]).values,
                              maker_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['メーカー'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞メーカー',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='食品・農林・水産',
                                             text='＜食品・農林・水産＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='建設・住宅・インテリア',
                                             text='＜建設・住宅・インテリア＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='繊維・化学・薬品・化粧品',
                                             text='＜繊維・化学・薬品・化粧品＞'+basic_text+str(empty_list[2]))
                           ]),
            CarouselColumn(title='＜業界＞メーカー',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='鉄鋼・金属・鉱業',
                                             text='＜鉄鋼・金属・鉱業＞'+basic_text+str(empty_list[3])),
                               MessageAction(label='機械・プラント',
                                             text='＜機械・プラント＞'+basic_text+str(empty_list[4])),
                               MessageAction(label='電子・電気機器',
                                             text='＜電子・電気機器＞'+basic_text+str(empty_list[5]))
                           ]),
            CarouselColumn(title='＜業界＞メーカー',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='自動車・輸送用機器',
                                             text='＜自動車・輸送用機器＞'+basic_text + str(empty_list[6])),
                               MessageAction(label='精密・医療用機器',
                                             text='＜精密・医療用機器＞'+basic_text + str(empty_list[7])),
                               MessageAction(label='印刷・事務機器関連',
                                             text='＜印刷・事務機器関連＞'+basic_text + str(empty_list[8]))
                           ]),
            CarouselColumn(title='＜業界＞メーカー',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='スポーツ・玩具・ゲーム',
                                             text='＜スポーツ・玩具・ゲーム＞'+basic_text + str(empty_list[9])),
                               MessageAction(label='その他', text=string),
                               MessageAction(label='---', text='他のボタンを押してください')
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'A1':
        empty_list = []
        service_list = ['不動産', '鉄道・航空・運輸・物流', '電力・ガス・エネルギー', 'フードサービス',
                        'ホテル・旅行', '医療・福祉', 'アミューズメント・レジャー', 'コンサルティング・調査',
                        '人材サービス', '教育']
        for service in service_list:
            true_index = sozo_df_permit['サービス・インフラ'].apply(lambda y: service in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['サービス・インフラ'].apply(lambda y: y.split(';')[-1]).values,
                              service_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['サービス・インフラ'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞サービス・インフラ',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='不動産',
                                             text='＜不動産＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='鉄道・航空・運輸・物流',
                                             text='＜鉄道・航空・運輸・物流＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='電力・ガス・エネルギー',
                                             text='＜電力・ガス・エネルギー＞'+basic_text+str(empty_list[2]))
                           ]),
            CarouselColumn(title='＜業界＞サービス・インフラ',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='フードサービス',
                                             text='＜フードサービス＞'+basic_text+str(empty_list[3])),
                               MessageAction(label='ホテル・旅行',
                                             text='＜ホテル・旅行＞'+basic_text+str(empty_list[4])),
                               MessageAction(label='医療・福祉',
                                             text='＜医療・福祉＞'+basic_text+str(empty_list[5]))
                           ]),
            CarouselColumn(title='＜業界＞サービス・インフラ',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='アミューズメント',
                                             text='＜アミューズメント＞'+basic_text + str(empty_list[6])),
                               MessageAction(label='コンサルティング・調査',
                                             text='＜コンサルティング・調査＞'+basic_text + str(empty_list[7])),
                               MessageAction(label='人材サービス',
                                             text='＜人材サービス＞'+basic_text + str(empty_list[8]))
                           ]),
            CarouselColumn(title='＜業界＞サービス・インフラ',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='教育',
                                             text='＜教育＞'+basic_text + str(empty_list[9])),
                               MessageAction(label='その他', text=string),
                               MessageAction(label='---', text='他のボタンを押してください')
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'A2':
        empty_list = []
        syosya_list = ['総合商社', '専門商社']
        for syosya in syosya_list:
            true_index = sozo_df_permit['商 社'].apply(lambda y: syosya in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['商 社'].apply(lambda y: y.split(';')[-1]).values,
                              syosya_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['商 社'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞商社',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='総合商社',
                                             text='＜総合商社＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='専門商社',
                                             text='＜専門商社＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='その他', text=string)
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'A3':
        empty_list = []
        software_list = ['ソフトウェア', 'インターネット', '通信']
        for software in software_list:
            true_index = sozo_df_permit['ソフトウェア'].apply(lambda y: software in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['ソフトウェア'].apply(lambda y: y.split(';')[-1]).values,
                              software_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['ソフトウェア'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞ソフトウェア',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='ソフトウェア',
                                             text='＜ソフトウェア＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='インターネット',
                                             text='＜インターネット＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='通信',
                                             text='＜通信＞'+basic_text+str(empty_list[2]))
                           ]),
            CarouselColumn(title='＜業界＞ソフトウェア',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='その他', text=string),
                               MessageAction(label='---', text='他のボタンを押してください'),
                               MessageAction(label='---', text='他のボタンを押してください')
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'A4':
        empty_list = []
        retail_list = ['百貨店', 'スーパー', 'コンビニ', '専門店']
        for retail in retail_list:
            true_index = sozo_df_permit['小売'].apply(lambda y: retail in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['小売'].apply(lambda y: y.split(';')[-1]).values,
                              retail_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['小売'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞小売',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='百貨店',
                                             text='＜百貨店＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='スーパー',
                                             text='＜スーパー＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='コンビニ',
                                             text='＜コンビニ＞'+basic_text+str(empty_list[2]))
                           ]),
            CarouselColumn(title='＜業界＞小売',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='専門店',
                                             text='＜専門店＞'+basic_text + str(empty_list[3])),
                               MessageAction(label='その他', text=string),
                               MessageAction(label='---', text='他のボタンを押してください')
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'A5':
        empty_list = []
        media_list = ['放送', '新聞', '出版', '広告']
        for media in media_list:
            true_index = sozo_df_permit['広告・出版・マスコミ	'].apply(lambda y: media in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['広告・出版・マスコミ	'].apply(lambda y: y.split(';')[-1]).values,
                              media_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['広告・出版・マスコミ	'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞広告・出版・マスコミ',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='放送',
                                             text='＜放送＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='新聞',
                                             text='＜新聞＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='出版',
                                             text='＜出版＞'+basic_text+str(empty_list[2]))
                           ]),
            CarouselColumn(title='＜業界＞広告・出版・マスコミ',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='広告',
                                             text='＜広告＞'+basic_text + str(empty_list[3])),
                               MessageAction(label='その他', text=string),
                               MessageAction(label='---', text='他のボタンを押してください')
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'A6':
        empty_list = []
        kinyu_list = ['銀行・証券', 'クレジット', '信販・リース', '生命・損保']
        for kinyu in kinyu_list:
            true_index = sozo_df_permit['金融'].apply(lambda y: kinyu in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['金融'].apply(lambda y: y.split(';')[-1]).values,
                              kinyu_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['金融'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞金融',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='銀行・証券',
                                             text='＜銀行・証券＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='クレジット',
                                             text='＜クレジット＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='信販・リース',
                                             text='＜信販・リース＞'+basic_text+str(empty_list[2]))
                           ]),
            CarouselColumn(title='＜業界＞金融',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='生命・損保',
                                             text='＜生命・損保＞'+basic_text + str(empty_list[3])),
                               MessageAction(label='その他', text=string),
                               MessageAction(label='---', text='他のボタンを押してください')
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'A7':
        empty_list = []
        kosha_list = ['公社・団体', '官公庁']
        for kosha in kosha_list:
            true_index = sozo_df_permit['官公庁・公社・団体'].apply(lambda y: kosha in y.split(';'))
            code_name = sozo_df_permit[true_index]['お名前'].values.tolist()
            empty_list.append(code_name)
        basic_text = '\n\n当該業界については以下の工房員に連絡してください\n（[]の場合、現在該当者無し）\n\n→ '

        others = np.setdiff1d(sozo_df_permit['官公庁・公社・団体'].apply(lambda y: y.split(';')[-1]).values,
                              kosha_list + ['該当なし'])
        if not bool(others.tolist()):
            string = '現在該当者は存在しません'
        else:
            string = '＜その他＞\n'
            for other in others:
                other_index = sozo_df_permit['官公庁・公社・団体'].apply(lambda y: other in y.split(';'))
                other_code = sozo_df_permit[other_index]['お名前'].values.tolist()
                add_string = '・' + other + ' → ' + str(other_code) + '\n'
                string += add_string
            string = string.rstrip('\n')

        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(title='＜業界＞官公庁・公社・団体',
                           text='（下記ボタンを押すと業界を志望した工房員コードが送信されます）',
                           actions=[
                               MessageAction(label='公社・団体',
                                             text='＜公社・団体＞'+basic_text+str(empty_list[0])),
                               MessageAction(label='官公庁',
                                             text='＜官公庁＞'+basic_text+str(empty_list[1])),
                               MessageAction(label='その他', text=string)
                           ])
        ])
        template_message = TemplateSendMessage(
            alt_text='alt_text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == 'B0':
        empty_list = []
        for site in ['マイナビ', 'リクナビ', 'unistyle', 'ONE CAREER', '就活ノート', 'Open Work',
                     'みんなの就職活動', '外資就活ドットコム', 'キャリタス就活', 'クリ博ナビ', '利用していない']:
            empty_list.append([site, sozo_df['サイト'].apply(lambda y: site in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜サイト名＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 利用就活サイト一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b0.png', dpi=250)
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

    elif text == 'B1':
        empty_list = []
        for book in ['絶対内定2021シリーズ', '就職活動が面白いほどうまくいく確実内定', '四季報', '最新！SPI3',
                     '史上最強SPI&テストセンター', '利用していない']:
            empty_list.append([book, sozo_df['本'].apply(lambda y: book in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜書籍名＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 利用就活本一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b1.png', dpi=250)
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

    elif text == 'B2':
        empty_list = []
        for agent in ['大学のキャリアセンター', 'マイナビ新卒紹介', 'リクナビ就職エージェント',
                      'キャリアチケット', '利用していない']:
            empty_list.append([agent, sozo_df['エージェント'].apply(lambda y: agent in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜エージェント名＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 利用エージェント一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b2.png', dpi=250)
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

    elif text == 'B3':
        empty_list = []
        for seminar in ['学内イベント', 'マイナビ就職EXPO', 'リクナビイベント', 'MeetsCompany', 'キャリアチケットラボ',
                      '就職エージェントneo', 'ジョブコミット', '利用していない']:
            empty_list.append([seminar, sozo_df['イベント・セミナー'].apply(lambda y: seminar in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list,
                          columns=['＜イベント・セミナー名＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 イベント・セミナー名一覧（回答数:{}名）'.format(sozo_df.shape[0]))
        plt.savefig('./static/test_b3.png', dpi=250)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_b3.png'

        others = np.setdiff1d(sozo_df['イベント・セミナー'].apply(lambda y: y.split(';')[-1]).values,
                              ['学内イベント', 'マイナビ就職EXPO', 'リクナビイベント', 'MeetsCompany', 'キャリアチケットラボ',
                               '就職エージェントneo', 'ジョブコミット', '利用していない'])
        send_text = '＜その他＞\n'
        for i in range(len(others)):
            if i == len(others)-1:
                send_text += '・{}'.format(others[i])
            else:
                send_text += '・{}\n'.format(others[i])

        line_bot_api.reply_message(event.reply_token,
                                   [ImageSendMessage(url, url), TextSendMessage(text=send_text)])

    elif text == 'C0':
        sozo_df_dropna = sozo_df.dropna(subset=['①業界'])
        empty_list = []
        for gyokai in ['メーカー', 'サービス・インフラ', '商社', 'ソフトウェア', '小売',
                       '広告・出版・マスコミ', '金融', '官公庁・公社・団体', 'その他']:
            empty_list.append([gyokai, sozo_df_dropna['①業界'].apply(lambda y: gyokai in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list,
                          columns=['＜業界名＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 インターン業界一覧（回答数:{}名）'.format(sozo_df_dropna.shape[0]))
        plt.savefig('./static/test_c0.png', dpi=250)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_c0.png'

        line_bot_api.reply_message(event.reply_token, ImageSendMessage(url, url))

    elif text == 'C1':
        sozo_df_dropna = sozo_df.dropna(subset=['時期'])
        empty_list = []
        for time in ['３年夏より前', '３年夏', '３年秋', '３年冬', '４年春', '４年夏']:
            empty_list.append([time, sozo_df_dropna['時期'].apply(lambda y: time in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list,
                          columns=['＜時期＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 インターン時期一覧（回答数:{}名）'.format(sozo_df_dropna.shape[0]))
        plt.savefig('./static/test_c1.png', dpi=250)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_c1.png'

        line_bot_api.reply_message(event.reply_token, ImageSendMessage(url, url))

    elif text == 'C2':
        sozo_df_dropna = sozo_df.dropna(subset=['期間'])
        empty_list = []
        for period in ['半日または1day', '2days', '3days〜1週間', '8日間以上2週間以内',
                       '15日間以上3週間以内', '3週間より長い']:
            empty_list.append([period, sozo_df_dropna['期間'].apply(lambda y: period in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list,
                          columns=['＜期間＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 インターン期間一覧（回答数:{}名）'.format(sozo_df_dropna.shape[0]))
        plt.savefig('./static/test_c2.png', dpi=250)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_c2.png'

        line_bot_api.reply_message(event.reply_token, ImageSendMessage(url, url))

    elif text == 'D0':
        sozo_df_dropna = sozo_df.dropna(subset=['人数'])
        empty_list = []
        for people in ['１〜５人', '６〜１０人', '１１人〜１５人', '１５人以上']:
            empty_list.append([people, sozo_df_dropna['人数'].apply(lambda y: people in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜人数＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 OB・OG訪問人数一覧（回答数:{}名）'.format(sozo_df_dropna.shape[0]))
        plt.savefig('./static/test_d0.png', dpi=250)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_d0.png'

        line_bot_api.reply_message(event.reply_token, ImageSendMessage(url, url))

    elif text == 'D1':
        sozo_df_dropna = sozo_df.dropna(subset=['人数'])
        empty_list = []
        for tool in ['もともとの知り合い、または知り合いを経由', '大学のOB・OG訪問システム', 'ビズリーチ・キャンパス',
                     'Matcher', 'レクミー']:
            empty_list.append([tool, sozo_df_dropna['使用ツール（複数回答可）'].apply(lambda y: tool in y).mean().round(3) * 100])

        df = pd.DataFrame(empty_list, columns=['＜使用ツール＞', '＜割合＞']).sort_values(by='＜割合＞', ascending=False)
        df['＜割合＞'] = df['＜割合＞'].astype(str).apply(lambda y: y[:4] + '%')
        df.index = np.arange(1, df.shape[0] + 1, 1)

        fig, ax = plt.subplots(figsize=(5.5, 2.5))
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, rowLabels=df.index, colLabels=df.columns,
                 loc='center', bbox=[0, 0, 1, 1], cellLoc='center')
        plt.title('工房員 OB・OG訪問使用ツール一覧（回答数:{}名）'.format(sozo_df_dropna.shape[0]))
        plt.savefig('./static/test_d1.png', dpi=250)
        url = 'https://sozo-recommendation.herokuapp.com' + '/static/test_d1.png'

        others = np.setdiff1d(sozo_df_dropna['使用ツール（複数回答可）'].apply(lambda y: y.split(';')[-1]).values,
                              ['もともとの知り合い、または知り合いを経由', '大学のOB・OG訪問システム', 'ビズリーチ・キャンパス',
                               'Matcher', 'レクミー'])
        send_text = '＜その他＞\n'
        for i in range(len(others)):
            if i == len(others)-1:
                send_text += '・{}'.format(others[i])
            else:
                send_text += '・{}\n'.format(others[i])

        line_bot_api.reply_message(event.reply_token,
                                   [ImageSendMessage(url, url), TextSendMessage(text=send_text)])

    elif text == 'version':
        about_version = 'Version 1.0.0\n' + '(Last Update: 2020-08-03)\n\n' + 'Developer: Kazuki Nishio'

    else:
        pass


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)
