# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.09,   yo.
# 2022.11.18 reviced,   yo.
# 2025.07.27 reviced,   yo.
#
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
#
# 動作確認
# Python 3.11.2 / debian12
# API v4r7
#
# 機能: 株価取得（ファイルにリストされた銘柄の株価をスナップショットで取得）

# 利用方法: 
# 事前に「e_api_login_tel.py」を実行して、
# 仮想URL（1日券）等を取得しておいてください。
# 「e_api_login_tel.py」と同じディレクトリで実行してください。
#
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文が出ます。
#   市場で約定した場合取り消せません。
# ==================================================
#

import urllib3
import datetime
import json
import time


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_account_property:
    def __init__(self):
        self.sUserId = ''           # userid
        self.sPassword = ''         # password
        self.sSecondPassword = ''   # 第2パスワード
        self.sUrl = ''              # 接続先URL
        self.sJsonOfmt = 5          # 返り値の表示形式指定
        
# ログイン属性クラス
class class_def_login_property:
    def __init__(self):
        self.p_no = 0                       # 累積p_no
        self.sJsonOfmt = ''                 # 返り値の表示形式指定
        self.sResultCode = ''               # 結果コード
        self.sResultText = ''               # 結果テキスト
        self.sZyoutoekiKazeiC = ''          # 譲渡益課税区分  1：特定  3：一般  5：NISA
        self.sSecondPasswordOmit = ''       # 暗証番号省略有無Ｃ  22.第二パスワード  APIでは第2暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sLastLoginDate = ''            # 最終ログイン日時
        self.sSogoKouzaKubun = ''           # 総合口座開設区分  0：未開設  1：開設
        self.sHogoAdukariKouzaKubun = ''    # 保護預り口座開設区分  0：未開設  1：開設
        self.sFurikaeKouzaKubun = ''        # 振替決済口座開設区分  0：未開設  1：開設
        self.sGaikokuKouzaKubun = ''        # 外国口座開設区分  0：未開設  1：開設
        self.sMRFKouzaKubun = ''            # ＭＲＦ口座開設区分  0：未開設  1：開設
        self.sTokuteiKouzaKubunGenbutu = '' # 特定口座区分現物  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiKouzaKubunSinyou = ''  # 特定口座区分信用  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiKouzaKubunTousin = ''  # 特定口座区分投信  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiHaitouKouzaKubun = ''  # 配当特定口座区分  0：未開設  1：開設
        self.sTokuteiKanriKouzaKubun = ''   # 特定管理口座開設区分  0：未開設  1：開設
        self.sSinyouKouzaKubun = ''         # 信用取引口座開設区分  0：未開設  1：開設
        self.sSakopKouzaKubun = ''          # 先物ＯＰ口座開設区分  0：未開設  1：開設
        self.sMMFKouzaKubun = ''            # ＭＭＦ口座開設区分  0：未開設  1：開設
        self.sTyukokufKouzaKubun = ''       # 中国Ｆ口座開設区分  0：未開設  1：開設
        self.sKawaseKouzaKubun = ''         # 為替保証金口座開設区分  0：未開設  1：開設
        self.sHikazeiKouzaKubun = ''        # 非課税口座開設区分  0：未開設  1：開設  ※ＮＩＳＡ口座の開設有無を示す。
        self.sKinsyouhouMidokuFlg = ''      # 金商法交付書面未読フラグ  1：未読（標準Ｗｅｂを起動し書面確認実行必須）  0：既読  ※未読の場合、ｅ支店・ＡＰＩは利用不可のため    仮想ＵＲＬは発行されず""を設定。  ※既読の場合、ｅ支店・ＡＰＩは利用可能となり    仮想ＵＲＬを発行し設定。  
        self.sUrlRequest = ''               # 仮想URL（REQUEST)  業務機能    （REQUEST I/F）仮想URL
        self.sUrlMaster = ''                # 仮想URL（MASTER)  マスタ機能  （REQUEST I/F）仮想URL
        self.sUrlPrice = ''                 # 仮想URL（PRICE)  時価情報機能（REQUEST I/F）仮想URL
        self.sUrlEvent = ''                 # 仮想URL（EVENT)  注文約定通知（EVENT I/F）仮想URL
        self.sUrlEventWebSocket = ''        # 仮想URL（EVENT-WebSocket)  注文約定通知（EVENT I/F WebSocket版）仮想URL
        self.sUpdateInformWebDocument = ''  # 交付書面更新予定日  標準Ｗｅｂの交付書面更新予定日決定後、該当日付を設定。  【注意】参照
        self.sUpdateInformAPISpecFunction = ''  # ｅ支店・ＡＰＩリリース予定日  ｅ支店・ＡＰＩリリース予定日決定後、該当日付を設定。  【注意】参照

        

# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char
        str_encode = str_encode + str_replace        
    return str_encode


# 機能： ファイルから文字情報を読み込み、その文字列を返す。
# 戻り値： 文字列
# 第１引数： ファイル名
# 備考： json形式のファイルを想定。
def func_read_from_file(str_fname):
    str_read = ''
    try:
        with open(str_fname, 'r', encoding = 'utf_8') as fin:
            while True:
                line = fin.readline()
                if not len(line):
                    break
                str_read = str_read + line
        return str_read
    except IOError as e:
        print('ファイルを読み込めません!!! ファイル名：',str_fname)
        print(type(e))


# 機能: ファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 出力するデータ
# 備考:
def func_write_to_file(str_fname_output, str_data):
    try:
        with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
            fout.write(str_data)
    except IOError as e:
        print('ファイルに書き込めません!!!  ファイル名：',str_fname_output)
        print(type(e))


# 機能: class_req型データをjson形式の文字列に変換する。
# 返値: json形式の文字
# 第１引数： class_req型データ
def func_make_json_format(work_class_req):
    work_key = ''
    work_value = ''
    str_json_data =  '{\n\t'
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
                str_json_data = str_json_data + work_class_req[i].str_key \
                                    + ':' + func_strip_dquot(work_value) \
                                    + ',\n\t'
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)
                str_json_data = str_json_data + func_check_json_dquat(work_class_req[i].str_key) \
                                    + ':' + work_value \
                                    + ',\n\t'
    str_json_data = str_json_data[:-3] + '\n}'
    return str_json_data


# 機能： API問合せ文字列を作成し返す。
# 戻り値： api問合せのurl文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第2引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    str_url = url_target
    if auth_flg == True :   # ログインの場合
        str_url = str_url + 'auth/'
    str_url = str_url + '?'
    str_url = str_url + func_make_json_format(work_class_req)
    return str_url


# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req


# 機能： アカウント情報をファイルから取得する
# 引数1: 口座情報を保存したファイル名
# 引数2: 口座情報（class_def_account_property型）データ
def func_get_acconut_info(fname, class_account_property):
    str_account_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_account_info = json.loads(str_account_info)

    class_account_property.sUserId = json_account_info.get('sUserId')
    class_account_property.sPassword = json_account_info.get('sPassword')
    class_account_property.sSecondPassword = json_account_info.get('sSecondPassword')
    class_account_property.sUrl = json_account_info.get('sUrl')

    # 返り値の表示形式指定
    class_account_property.sJsonOfmt = json_account_info.get('sJsonOfmt')
    # "5"は "1"（1ビット目ON）と”4”（3ビット目ON）の指定となり
    # ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定


# 機能： ログイン情報をファイルから取得する
# 引数1: ログイン情報を保存したファイル名（fname_login_response = "e_api_login_response.txt"）
# 引数2: ログインデータ型（class_def_login_property型）
def func_get_login_info(str_fname, class_login_property):
    str_login_respons = func_read_from_file(str_fname)
    dic_login_respons = json.loads(str_login_respons)

    class_login_property.sResultCode = dic_login_respons.get('sResultCode')                 # 結果コード
    class_login_property.sResultText = dic_login_respons.get('sResultText')                 # 結果テキスト
    class_login_property.sZyoutoekiKazeiC = dic_login_respons.get('sZyoutoekiKazeiC')       # 譲渡益課税区分  1：特定  3：一般  5：NISA
    class_login_property.sSecondPasswordOmit = dic_login_respons.get('sSecondPasswordOmit')     # 暗証番号省略有無Ｃ
    class_login_property.sLastLoginDate = dic_login_respons.get('sLastLoginDate')               # 最終ログイン日時
    class_login_property.sSogoKouzaKubun = dic_login_respons.get('sSogoKouzaKubun')             # 総合口座開設区分  0：未開設  1：開設
    class_login_property.sHogoAdukariKouzaKubun = dic_login_respons.get('sHogoAdukariKouzaKubun')       # 保護預り口座開設区分  0：未開設  1：開設
    class_login_property.sFurikaeKouzaKubun = dic_login_respons.get('sFurikaeKouzaKubun')               # 振替決済口座開設区分  0：未開設  1：開設
    class_login_property.sGaikokuKouzaKubun = dic_login_respons.get('sGaikokuKouzaKubun')               # 外国口座開設区分  0：未開設  1：開設
    class_login_property.sMRFKouzaKubun = dic_login_respons.get('sMRFKouzaKubun')                       # ＭＲＦ口座開設区分  0：未開設  1：開設
    class_login_property.sTokuteiKouzaKubunGenbutu = dic_login_respons.get('sTokuteiKouzaKubunGenbutu') # 特定口座区分現物  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiKouzaKubunSinyou = dic_login_respons.get('sTokuteiKouzaKubunSinyou')   # 特定口座区分信用  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiKouzaKubunTousin = dic_login_respons.get('sTokuteiKouzaKubunTousin')   # 特定口座区分投信  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiHaitouKouzaKubun = dic_login_respons.get('sTokuteiHaitouKouzaKubun')   # 配当特定口座区分  0：未開設  1：開設
    class_login_property.sTokuteiKanriKouzaKubun = dic_login_respons.get('sTokuteiKanriKouzaKubun')     # 特定管理口座開設区分  0：未開設  1：開設
    class_login_property.sSinyouKouzaKubun = dic_login_respons.get('sSinyouKouzaKubun')         # 信用取引口座開設区分  0：未開設  1：開設
    class_login_property.sSinyouKouzaKubun = dic_login_respons.get('sSinyouKouzaKubun')         # 信用取引口座開設区分  0：未開設  1：開設
    class_login_property.sSakopKouzaKubun = dic_login_respons.get('sSakopKouzaKubun')           # 先物ＯＰ口座開設区分  0：未開設  1：開設
    class_login_property.sMMFKouzaKubun = dic_login_respons.get('sMMFKouzaKubun')               # ＭＭＦ口座開設区分  0：未開設  1：開設
    class_login_property.sTyukokufKouzaKubun = dic_login_respons.get('sTyukokufKouzaKubun')     # 中国Ｆ口座開設区分  0：未開設  1：開設
    class_login_property.sKawaseKouzaKubun = dic_login_respons.get('sKawaseKouzaKubun')         # 為替保証金口座開設区分  0：未開設  1：開設
    class_login_property.sHikazeiKouzaKubun = dic_login_respons.get('sHikazeiKouzaKubun')       # 非課税口座開設区分  0：未開設  1：開設  ※ＮＩＳＡ口座の開設有無を示す。
    class_login_property.sKinsyouhouMidokuFlg = dic_login_respons.get('sKinsyouhouMidokuFlg')   # 金商法交付書面未読フラグ  1：未読（標準Ｗｅｂを起動し書面確認実行必須）  0：既読  ※未読の場合、ｅ支店・ＡＰＩは利用不可のため    仮想ＵＲＬは発行されず""を設定。  ※既読の場合、ｅ支店・ＡＰＩは利用可能となり    仮想ＵＲＬを発行し設定。  
    class_login_property.sUrlRequest = dic_login_respons.get('sUrlRequest')     # 仮想URL（REQUEST)  業務機能    （REQUEST I/F）仮想URL
    class_login_property.sUrlMaster = dic_login_respons.get('sUrlMaster')       # 仮想URL（MASTER)  マスタ機能  （REQUEST I/F）仮想URL
    class_login_property.sUrlPrice = dic_login_respons.get('sUrlPrice')         # 仮想URL（PRICE)  時価情報機能（REQUEST I/F）仮想URL
    class_login_property.sUrlEvent = dic_login_respons.get('sUrlEvent')         # 仮想URL（EVENT)  注文約定通知（EVENT I/F）仮想URL
    class_login_property.sUrlEventWebSocket = dic_login_respons.get('sUrlEventWebSocket')    # 仮想URL（EVENT-WebSocket)  注文約定通知（EVENT I/F WebSocket版）仮想URL
    class_login_property.sUpdateInformWebDocument = dic_login_respons.get('sUpdateInformWebDocument')    # 交付書面更新予定日  標準Ｗｅｂの交付書面更新予定日決定後、該当日付を設定。  【注意】参照
    class_login_property.sUpdateInformAPISpecFunction = dic_login_respons.get('sUpdateInformAPISpecFunction')    # ｅ支店・ＡＰＩリリース予定日  ｅ支店・ＡＰＩリリース予定日決定後、該当日付を設定。  【注意】参照
    

# 機能： p_noをファイルから取得する
# 引数1: p_noを保存したファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: login情報（class_def_login_property型）データ
def func_get_p_no(fname, class_login_property):
    str_p_no_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_p_no_info = json.loads(str_p_no_info)
    class_login_property.p_no = int(json_p_no_info.get('p_no'))
        
    
# 機能: p_noを保存するためのjson形式のテキストデータを作成します。
# 引数1: p_noを保存するファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: 保存するp_no
# 備考:
def func_save_p_no(str_fname_output, int_p_no):
    # "p_no"を保存する。
    str_info_p_no = '{\n'
    str_info_p_no = str_info_p_no + '\t' + '"p_no":"' + str(int_p_no) + '"\n'
    str_info_p_no = str_info_p_no + '}\n'
    func_write_to_file(str_fname_output, str_info_p_no)
    print('現在の"p_no"を保存しました。 p_no =', int_p_no)            
    print('ファイル名:', str_fname_output)

#--- 以上 共通コード -------------------------------------------------









# 「型＋情報コード」から「名前」を取得する
# 引数：型＋情報コード」（string）
# 戻り値：「名前」（string）
# 資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」（api_event_if.pdf）
# p6-9/26 【情報コード一覧】
def func_code_to_name(str_input):
    str_input = func_strip_dquot(str_input)
    str_return = ''
    if str_input == 'xLISS':        str_return = '"所属"'         # ShiftJIS文字列を１６進数文字列として設定。（含む半角カナ）
    elif str_input == 'pDPP':       str_return = '"現在値"'        # 
    elif str_input == 'tDPP:T':     str_return = '"現在値時刻"'    # 「HH:MM」
    elif str_input == 'pDPG':       str_return = '"現値前値比較"' # ,「0000」：事象なし「0056」：現値＝前値,「0057」：現値＞前値（↑）,「0058」：現値＜前値(↓),「0059」：中断板寄後の初値「0060」：ザラバ引け（・）,「0061」：板寄引け「0062」：中断引け,「0068」：売買停止引け※（）内は画面表示記号。
    elif str_input == 'pDYWP':      str_return = '"前日比"'        # 
    elif str_input == 'pDYRP':      str_return = '"騰落率"'        # 
    elif str_input == 'pDOP':       str_return = '"始値"'         # 
    elif str_input == 'tDOP:T':     str_return = '"始値時刻"'   # 「HH:MM」
    elif str_input == 'pDHP':       str_return = '"高値"'         # 
    elif str_input == 'tDHP:T':     str_return = '"高値時刻"'   # 「HH:MM」
    elif str_input == 'pDLP':       str_return = '"安値"'         # 
    elif str_input == 'tDLP:T':     str_return = '"安値時刻"'   # 「HH:MM」
    elif str_input == 'pDV':        str_return = '"出来高"'        # 
    elif str_input == 'pQAS':       str_return = '"売気配値種類"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（ウ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（U）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == 'pQAP':       str_return = '"売気配値"'    # 
    elif str_input == 'pAV':        str_return = '"売気配数量"'    # 
    elif str_input == 'pQBS':       str_return = '"買気配値種類"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（カ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（K）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == 'pQBP':       str_return = '"買気配値"'    # 
    elif str_input == 'pBV':        str_return = '"買気配数量"'    # 
    elif str_input == 'xDVES':      str_return = '"配当落銘柄区分"'    # 「配」：配当権利落、中間配当権利落、期中配当権利落,「」：上記外,※「」内文字を画面表示。
    elif str_input == 'xDCFS':      str_return = '"不連続要因銘柄区分"'    # 「分」：株式分割,「併」：株式併合、減資を伴う併合,「有」：有償,「無」：無償,「預」権利預り証落ち,「ム」：無償割当,「ラ」：ライツオファリング,「」：上記外,※「」内文字を画面表示。
    elif str_input == 'pDHF':       str_return = '"日通し高値フラグ"'    # 「0000」：事象なし,「0071」：ストップ高(S),
    elif str_input == 'pDLF':       str_return = '"日通し安値フラグ"'    # 「0000」：事象なし,「0072」：ストップ安(S), ※（）内は画面表示記号。
    elif str_input == 'pDJ':        str_return = '"売買代金"'    # 
    elif str_input == 'pAAV':       str_return = '"売数量（成行）"'    # 
    elif str_input == 'pABV':       str_return = '"買数量（成行）"'    # 
    elif str_input == 'pQOV':       str_return = '"売-OVER"'    # 
    elif str_input == 'pGAV10':     str_return = '"売-１０-数量"'    # 
    elif str_input == 'pGAP10':     str_return = '"売-１０-値段"'    # 
    elif str_input == 'pGAV9':      str_return = '"売-９-数量"'    # 
    elif str_input == 'pGAP9':      str_return = '"売-９-値段"'    # 
    elif str_input == 'pGAV8':      str_return = '"売-８-数量"'    # 
    elif str_input == 'pGAP8':      str_return = '"売-８-値段"'    # 
    elif str_input == 'pGAV7':      str_return = '"売-７-数量"'    # 
    elif str_input == 'pGAP7':      str_return = '"売-７-値段"'    # 
    elif str_input == 'pGAV6':      str_return = '"売-６-数量"'    # 
    elif str_input == 'pGAP6':      str_return = '"売-６-値段"'    # 
    elif str_input == 'pGAV5':      str_return = '"売-５-数量"'    # 
    elif str_input == 'pGAP5':      str_return = '"売-５-値段"'    # 
    elif str_input == 'pGAV4':      str_return = '"売-４-数量"'    # 
    elif str_input == 'pGAP4':      str_return = '"売-４-値段"'    # 
    elif str_input == 'pGAV3':      str_return = '"売-３-数量"'    # 
    elif str_input == 'pGAP3':      str_return = '"売-３-値段"'    # 
    elif str_input == 'pGAV2':      str_return = '"売-２-数量"'    # 
    elif str_input == 'pGAP2':      str_return = '"売-２-値段"'    # 
    elif str_input == 'pGAV1':      str_return = '"売-１-数量"'    # 
    elif str_input == 'pGAP1':      str_return = '"売-１-値段"'    # 
    elif str_input == 'pGBV1':      str_return = '"買-１-数量"'    # 
    elif str_input == 'pGBP1':      str_return = '"買-１-値段"'    # 
    elif str_input == 'pGBV2':      str_return = '"買-２-数量"'    # 
    elif str_input == 'pGBP2':      str_return = '"買-２-値段"'    # 
    elif str_input == 'pGBV3':      str_return = '"買-３-数量"'    # 
    elif str_input == 'pGBP3':      str_return = '"買-３-値段"'    # 
    elif str_input == 'pGBV4':      str_return = '"買-４-数量"'    # 
    elif str_input == 'pGBP4':      str_return = '"買-４-値段"'    # 
    elif str_input == 'pGBV5':      str_return = '"買-５-数量"'    # 
    elif str_input == 'pGBP5':      str_return = '"買-５-値段"'    # 
    elif str_input == 'pGBV6':      str_return = '"買-６-数量"'    # 
    elif str_input == 'pGBP6':      str_return = '"買-６-値段"'    # 
    elif str_input == 'pGBV7':      str_return = '"買-７-数量"'    # 
    elif str_input == 'pGBP7':      str_return = '"買-７-値段"'    # 
    elif str_input == 'pGBV8':      str_return = '"買-８-数量"'    # 
    elif str_input == 'pGBP8':      str_return = '"買-８-値段"'    # 
    elif str_input == 'pGBV9':      str_return = '"買-９-数量"'    # 
    elif str_input == 'pGBP9':      str_return = '"買-９-値段"'    # 
    elif str_input == 'pGBV10':     str_return = '"買-１０-数量"'    # 
    elif str_input == 'pGBP10':     str_return = '"買-１０-値段"'    # 
    elif str_input == 'pQUV':       str_return = '"買-UNDER"'        # 
    elif str_input == 'pVWAP':      str_return = '"VWAP"'    # 
    elif str_input == 'pPRP':       str_return = '"前日終値"'    # 
    else:                           str_return = 'none'

    return  str_return
        

# 「名前」から「型＋情報コード」を取得する
# 引数：「名前」（string）
# 戻り値：型＋情報コード」（string）
# 資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」（api_event_if.pdf）
# p6-9/26 【情報コード一覧】
def func_name_to_code(str_input):
    str_input = func_strip_dquot(str_input)
    str_return = ''
    if str_input == '所属':        str_return = '" xLISS"'    # ShiftJIS文字列を１６進数文字列として設定。（含む半角カナ）
    elif str_input == '現在値':        str_return = '"pDPP"'    # 
    elif str_input == '現在値時刻':        str_return = '"tDPP:T"'    # 「HH:MM」
    elif str_input == '現値前値比較':        str_return = '"pDPG"'    # 「0000」：事象なし「0056」：現値＝前値,「0057」：現値＞前値（↑）,「0058」：現値＜前値(↓),「0059」：中断板寄後の初値「0060」：ザラバ引け（・）,「0061」：板寄引け「0062」：中断引け,「0068」：売買停止引け※（）内は画面表示記号。
    elif str_input == '前日比':        str_return = '"pDYWP"'    # 
    elif str_input == '騰落率':        str_return = '"pDYRP"'    # 
    elif str_input == '始値':        str_return = '"pDOP"'    # 
    elif str_input == '始値時刻':        str_return = '"tDOP:T"'    # 「HH:MM」
    elif str_input == '高値':        str_return = '"pDHP"'    # 
    elif str_input == '高値時刻':        str_return = '"tDHP:T"'    # 「HH:MM」
    elif str_input == '安値':        str_return = '"pDLP"'    # 
    elif str_input == '安値時刻':        str_return = '"tDLP:T"'    # 「HH:MM」
    elif str_input == '出来高':        str_return = '"pDV"'    # 
    elif str_input == '売気配値種類':        str_return = '"pQAS"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（ウ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（U）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == '売気配値':        str_return = '"pQAP"'    # 
    elif str_input == '売気配数量':        str_return = '"pAV"'    # 
    elif str_input == '買気配値種類':        str_return = '"pQBS"'    # 「0000」：事象なし,「0101」：一般気配,「0102」：特別気配（カ）,「0107」：寄前気配（寄）,「0108」：停止前特別気配（停）,「0118」：連続約定気配,「0119」：停止前の連続約定気配（K）,「0120」：一般気配、買上がり・売下がり中,※（）内は画面表示記号。
    elif str_input == '買気配値':        str_return = '"pQBP"'    # 
    elif str_input == '買気配数量':        str_return = '"pBV"'    # 
    elif str_input == '配当落銘柄区分':        str_return = '"xDVES"'    # 「配」：配当権利落、中間配当権利落、期中配当権利落,「」：上記外,※「」内文字を画面表示。
    elif str_input == '不連続要因銘柄区分':        str_return = '"xDCFS"'    # 「分」：株式分割,「併」：株式併合、減資を伴う併合,「有」：有償,「無」：無償,「預」権利預り証落ち,「ム」：無償割当,「ラ」：ライツオファリング,「」：上記外,※「」内文字を画面表示。
    elif str_input == '日通し高値フラグ':        str_return = '"pDHF"'    # 「0000」：事象なし,「0071」：ストップ高(S),
    elif str_input == '日通し安値フラグ':        str_return = '"pDLF"'    # 「0000」：事象なし,「0072」：ストップ安(S), ※（）内は画面表示記号。
    elif str_input == '売買代金':        str_return = '"pDJ"'    # 
    elif str_input == '売数量（成行）':        str_return = '"pAAV"'    # 
    elif str_input == '買数量（成行）':        str_return = '"pABV"'    # 
    elif str_input == '売-OVER':        str_return = '"pQOV"'    # 
    elif str_input == '売-１０-数量':      str_return = '"pGAV10"'    # 
    elif str_input == '売-１０-値段':      str_return = '"pGAP10"'    # 
    elif str_input == '売-９-数量':        str_return = '"pGAV9"'    # 
    elif str_input == '売-９-値段':        str_return = '"pGAP9"'    # 
    elif str_input == '売-８-数量':        str_return = '"pGAV8"'    # 
    elif str_input == '売-８-値段':        str_return = '"pGAP8"'    # 
    elif str_input == '売-７-数量':        str_return = '"pGAV7"'    # 
    elif str_input == '売-７-値段':        str_return = '"pGAP7"'    # 
    elif str_input == '売-６-数量':        str_return = '"pGAV6"'    # 
    elif str_input == '売-６-値段':        str_return = '"pGAP6"'    # 
    elif str_input == '売-５-数量':        str_return = '"pGAV5"'    # 
    elif str_input == '売-５-値段':        str_return = '"pGAP5"'    # 
    elif str_input == '売-４-数量':        str_return = '"pGAV4"'    # 
    elif str_input == '売-４-値段':        str_return = '"pGAP4"'    # 
    elif str_input == '売-３-数量':        str_return = '"pGAV3"'    # 
    elif str_input == '売-３-値段':        str_return = '"pGAP3"'    # 
    elif str_input == '売-２-数量':        str_return = '"pGAV2"'    # 
    elif str_input == '売-２-値段':        str_return = '"pGAP2"'    # 
    elif str_input == '売-１-数量':        str_return = '"pGAV1"'    # 
    elif str_input == '売-１-値段':        str_return = '"pGAP1"'    # 
    elif str_input == '買-１-数量':        str_return = '"pGBV1"'    # 
    elif str_input == '買-１-値段':        str_return = '"pGBP1"'    # 
    elif str_input == '買-２-数量':        str_return = '"pGBV2"'    # 
    elif str_input == '買-２-値段':        str_return = '"pGBP2"'    # 
    elif str_input == '買-３-数量':        str_return = '"pGBV3"'    # 
    elif str_input == '買-３-値段':        str_return = '"pGBP3"'    # 
    elif str_input == '買-４-数量':        str_return = '"pGBV4"'    # 
    elif str_input == '買-４-値段':        str_return = '"pGBP4"'    # 
    elif str_input == '買-５-数量':        str_return = '"pGBV5"'    # 
    elif str_input == '買-５-値段':        str_return = '"pGBP5"'    # 
    elif str_input == '買-６-数量':        str_return = '"pGBV6"'    # 
    elif str_input == '買-６-値段':        str_return = '"pGBP6"'    # 
    elif str_input == '買-７-数量':        str_return = '"pGBV7"'    # 
    elif str_input == '買-７-値段':        str_return = '"pGBP7"'    # 
    elif str_input == '買-８-数量':        str_return = '"pGBV8"'    # 
    elif str_input == '買-８-値段':        str_return = '"pGBP8"'    # 
    elif str_input == '買-９-数量':        str_return = '"pGBV9"'    # 
    elif str_input == '買-９-値段':        str_return = '"pGBP9"'    # 
    elif str_input == '買-１０-数量':      str_return = '"pGBV10"'    # 
    elif str_input == '買-１０-値段':      str_return = '"pGBP10"'    # 
    elif str_input == '買-UNDER':          str_return = '"pQUV"'    # 
    elif str_input == 'VWAP':               str_return = '"pVWAP"'    # 
    elif str_input == '前日終値':          str_return = '"pPRP"'    # 
    else:       str_return = 'none'

    return str_return




# 株価取得リストの読み込み
# 引数：ファイル名、銘柄コード保存用配列、取得する情報コード用配列
# 指定ファイルを開き、1行目で取得する情報コードを読み込み、2行目以降で銘柄コードを読み込む。
# （通常1行目の）情報コードを読み込む行の第1項目は、'stock_code'とすることが必要。
def func_read_price_list(str_fname_input, my_code, my_column):
    try:
        # 入力データを読み込み処理開始
        with open(str_fname_input, 'r', encoding = 'shift_jis') as fin:
            print('file read ok -----', str_fname_input)
                            
            while True:
                line = fin.readline()
                
                if not len(line):
                    #EOFの場合
                    break

                # 行のデータをcsvの「,」で分割し必要なフィールドを読み込む。
                sprit_out = line.split(',')
                
                if len(sprit_out) > 0:
                    if len(sprit_out[0]) > 0 and func_strip_dquot(sprit_out[0]) == 'stock_code':
                        # １行目は表題行なので、情報コードを取得する。
                        # 取得できる価格情報は、資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」
                        # p6-8/26 【情報コード一覧】を利用する。
                        # 取得コードの書式：型+情報コード
                        
                        for i in range(1,len(sprit_out)):
                            my_column.append('')
                            my_column[i] = func_strip_dquot(sprit_out[i])

                        # 銘柄コードのリストの最初の項目に、便宜上'stock_code'を入れておく。
                        my_code[-1] = func_strip_dquot(sprit_out[0])
                            
                    elif  len(sprit_out[0]) > 0 :
                        my_code.append('')
                        my_code[-1] = func_strip_dquot(sprit_out[0])
                        
                    else:
                        pass
                                    
    except IOError as e:
        print('File Not Found!!!')
        print(type(e))
        #print(line)




# １行目タイトルを株価情報のファイルに書き込む
# 引数：出力ファイル名、取得した株価情報（辞書型）、取得する情報コード用配列
# 指定ファイルを開き、1行目に取得する情報名を書き込み、2行目以降で取得した情報を書き込む。
def func_write_price_title(str_fname_output, my_column):
    try:
        with open(str_fname_output, 'w', encoding = 'shift_jis') as fout:
            print('file open at w, "fout": ', str_fname_output )
            # 出力ファイルの１行目の列名を作成
            str_text_out = 'stock_code'
            for i in range(len(my_column)):
                if len(my_column[i]) > 0 :
                    str_text_out = str_text_out + ',' + func_code_to_name(my_column[i])     # 情報コードを名前に変換。
            str_text_out = str_text_out + '\n'
            fout.write(str_text_out)     # １行目に列名を書き込む

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))
        #print(line)




# 取得した株価情報を追記モードでファイルに書き込む
# 引数：出力ファイル名、取得した株価情報（辞書型）、取得する情報コード用配列
# 指定ファイルを開き、1行目に取得する情報名を書き込み、2行目以降で取得した情報を書き込む。
def func_write_price_list(str_fname_output, dic_return, my_column):
    try:
        with open(str_fname_output, 'a', encoding = 'shift_jis') as fout:
            print('file open at a, "fout": ', str_fname_output )
            # 取得した情報から行データを作成し書き込む
            str_text_out = ''
            for i in range(len(dic_return)):
                # 行データ作成
                str_sIssueCode = dic_return[i].get('sIssueCode') 
                if not str_sIssueCode == 'stock_code' :
                    str_text_out = str_sIssueCode
                    for n in range(len(my_column)):
                        if len(my_column[n]) > 0 :
                            str_text_out = str_text_out + ',' + dic_return[i].get(my_column[n])
                    str_text_out = str_text_out + '\n'
                    fout.write(str_text_out)     # 処理済みの株価データを書き込む
                  

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))
        #print(line)




# 株価情報の取得
# 引数：銘柄コード（配列）, 取得する「情報コード」（配列）, 口座属性クラス
# マニュアル「ｅ支店・ＡＰＩ、ブラウザからの利用方法」の「時価」シートの時価関連情報取得サンプル
#
# ３．利用方法（２）時価関連情報の取得
# https://10.62.26.91/e_api_v4r2/request/MDExNDczNTEwMDQwNi05MS02NDU1NA==/?{"p_no":"20","p_sd_date":"2021.06.04-14:56:50.000",
# "sCLMID":"CLMMfdsGetMarketPrice","sTargetIssueCode":"6501,6501,101","sTargetColumn":"pDPP,tDPP:T,pPRP","sJsonOfmt":"5"}
#
# 
# 取得できる価格情報は、資料「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」
# p6-8/26 【情報コード一覧】を利用する。
# 取得コードの書式：型+情報コード
#
# 株価の取得は通信帯域に負荷が掛かります。利用する情報のみの取得をお願いいたします。
def func_get_price(int_p_no, str_code_list, my_column, class_login_property):

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sCLMID"'
    str_value = '"CLMMfdsGetMarketPrice"'   # 株価取得を指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 株価を取得する銘柄コードをセット
    # 取得したい銘柄コードをカンマで区切りで羅列する。
    # 例：{"sTargetIssueCode":"6501,6502,101"}
    str_key = '"sTargetIssueCode"'
    str_value = str_code_list
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    

    # 取得する「情報コード」をセット
    # 取得したい情報コードをカンマで区切りで羅列する。	
    # 例：{"sTargetColumn":"pDPP,tDPP:T,pPRP"}
    str_list = ''
    for i in range(len(my_column)):
        if len(my_column[i]) > 0:
            str_list = str_list + my_column[i] + ','
        
    str_key = '"sTargetColumn"'
    str_value = str_list[:-1]
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_login_property.sJsonOfmt
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_login_property.sUrlPrice, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)

    return json_return




    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================



if __name__ == "__main__":

    # --- 利用時に変数を設定してください -------------------------------------------------------
    # コマンド用パラメーター -------------------    
    #
    str_fname_input = 'price_list_in.csv'   # 取得する情報コードと銘柄を読み込むファイル名。カレントディレクトリに存在すること。
    str_fname_output = 'price_list_out.csv'   # 書き込むファイル名。カレントディレクトリに上書きモードでファイルが作成される。


    # --- 以上設定項目 -------------------------------------------------------------------------

    # --- ファイル名等を設定（実行ファイルと同じディレクトリ） ---------------------------------------
    fname_account_info = "./e_api_account_info.txt"
    fname_login_response = "./e_api_login_response.txt"
    fname_info_p_no = "./e_api_info_p_no.txt"
    # --- 以上ファイル名設定 -------------------------------------------------------------------------

    my_account_property = class_def_account_property()
    my_login_property = class_def_login_property()
    
    # 口座情報をファイルから読み込む。
    func_get_acconut_info(fname_account_info, my_account_property)
    
    # ログイン応答を保存した「e_api_login_response.txt」から、仮想URLと課税flgを取得
    func_get_login_info(fname_login_response, my_login_property)

    
    my_login_property.sJsonOfmt = my_account_property.sJsonOfmt                   # 返り値の表示形式指定
    my_login_property.sSecondPassword = func_replace_urlecnode(my_account_property.sSecondPassword)        # 22.第二パスワード  APIでは第2暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
    
    # 現在（前回利用した）のp_noをファイルから取得する
    func_get_p_no(fname_info_p_no, my_login_property)
    my_login_property.p_no = my_login_property.p_no + 1
    # "p_no"を保存する。
    func_save_p_no(fname_info_p_no, my_login_property.p_no)

    print()
    print('-- 株価の照会 ファイル読み込み、ファイル書き出し-------------------------------------------------------------')
    # マニュアル「ｅ支店・ＡＰＩ、ブラウザからの利用方法」の「時価」シートの時価関連情報取得サンプル
    # ３．利用方法（２）時価関連情報の取得
    # https://10.62.26.91/e_api_v4r2/request/MDExNDczNTEwMDQwNi05MS02NDU1NA==/?{"p_no":"20","p_sd_date":"2021.06.04-14:56:50.000",
    # "sCLMID":"CLMMfdsGetMarketPrice","sTargetIssueCode":"6501,6501,101","sTargetColumn":"pDPP,tDPP:T,pPRP","sJsonOfmt":"5"}
    # この例を参考に投げるurlを作成する。

    req_item = [class_req()]
    my_column = ['']
    my_code = ['']

    # ファイルから取得する情報コードと銘柄を読み込む。
    func_read_price_list(str_fname_input, my_code, my_column)

    # 株価情報の出力ファイルに１行目タイトルを書き込む。
    func_write_price_title(str_fname_output, my_column)

    start_time = datetime.datetime.now()    # 開始時刻計測

    str_code_list = ''
    i = 0
    j = 0
    int_set = 0
    # v4r3 より、株価取得は1度に120銘柄までに変更となった。
    while j < len(my_code):
        if len(my_code[j]) > 0 and not my_code[j] == 'stock_code' :
            str_code_list = str_code_list + my_code[j] + ','
        if i >= 119 :
            str_code_list = str_code_list[:-1]
            my_login_property.p_no = my_login_property.p_no + 1
            # 株価を取得。
            dic_return = func_get_price(my_login_property.p_no, str_code_list, my_column, my_login_property)
            if dic_return is not None:
                # 応答がエラーでない場合
                if dic_return.get('p_errno') != '-2' and dic_return.get('p_errno') != '2':
                    # 株価情報部分を辞書型で抜き出す。
                    list_return = dic_return.get('aCLMMfdsMarketPrice')
                    if list_return is not None:
                        # 取得した株価情報を追記モードでファイルに書き込む。
                        func_write_price_list(str_fname_output, list_return, my_column)
                else:
                    print()
                    print('p_errno:', dic_return.get('p_errno'))
                    print('p_err:', dic_return.get('p_err'))
                    print()
                    print("仮想URLが有効ではありません。")
                    print("電話認証 + e_api_login_tel.py実行")
                    print("を再度行い、新しく仮想URL（1日券）を取得してください。")
                    print()    
                    print()    
            else:
                print('APIの応答がNone')
                print("APIの応答が正常ではありません。")
                print()    
                print()    

            # 120銘柄で初期化            
            i = 0
            int_set = int_set + 1
            str_code_list = ''
        else:
            i = i + 1
        j = int_set * 120 + i
        
    if len(str_code_list) > 0 :
        str_code_list = str_code_list[:-1]
        my_login_property.p_no = my_login_property.p_no + 1
        # 株価を取得。
        dic_return = func_get_price(my_login_property.p_no, str_code_list, my_column, my_login_property)

        finish_time = datetime.datetime.now()    # 終了時刻計測
        delta_time = finish_time - start_time
        # print('delta_time= ', delta_time, ' ← 株価取得時間')

        if dic_return is not None:
            # 応答がエラーでない場合
            if dic_return.get('p_errno') != '-2' and dic_return.get('p_errno') != '2':
                # 株価情報部分を辞書型で抜き出す。
                list_return = dic_return.get('aCLMMfdsMarketPrice')
                if list_return is not None:
                    # 取得した株価情報を追記モードでファイルに書き込む。
                    func_write_price_list(str_fname_output, list_return, my_column)
            else:
                print()
                print('p_errno:', dic_return.get('p_errno'))
                print('p_err:', dic_return.get('p_err'))
                print()
                print("仮想URLが有効ではありません。")
                print("電話認証 + e_api_login_tel.py実行")
                print("を再度行い、新しく仮想URL（1日券）を取得してください。")
                print()    
                print()    
        else:
            print('APIの応答がNone')
            print("APIの応答が正常ではありません。")
            print()    
            print()    
    
    my_login_property.p_no = my_login_property.p_no
    print()    
    print()    
    # "p_no"を保存する。
    func_save_p_no(fname_info_p_no, my_login_property.p_no)

