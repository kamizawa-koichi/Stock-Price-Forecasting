import time
import numpy as np
import pandas as pd
import streamlit as st
import pandas_datareader as web
import plotly.graph_objects as go
from PIL import Image
from datetime import date, datetime, timedelta

# アプリの概要の説明
st.title('Finance App.')

st.write("""
    こちらは株価可視化ツールです。（※読み込みに時間がかかる場合があります。）

    ここでは、  
    ・主要な株価・ファイナンス指標  
    ・日経225銘柄の詳細な株価チャート（90日間）  
    ・2020/01/01~本日までにおける株価推移の比較  
    を確認することができます。""")

# __________________________________________________________________________

# 主要な指標を表示させる
import requests
from bs4 import BeautifulSoup

#yahooからスクレイピング
url = 'https://finance.yahoo.co.jp/'
res = requests.get(url)

soup = BeautifulSoup(res.text, 'html.parser')
rate_list =[]
rates = soup.find_all('span', attrs={'class': '_3rXWJKZF'})

rate = rates[0]
importance = float(rate.text.replace(',', ''))

details = []

#リストの最後５行が、日経・NYダウの価格・前日変化、米ドルとなっている
for rate in rates[-5:]:
    importance = float(rate.text.replace(',', ''))
    details.append(importance)

st.write("""##   """) #行間調整

st.write("""### ・主要な株価・ファイナンス指標 """)
col1, col2, col3 = st.columns(3)
col1.metric(label="日経平均株価", value=details[0], delta=details[1])
col2.metric(label="NYダウ", value=details[2], delta=details[3])
col3.metric(label='米ドル/円', value=details[4])

# __________________________________________________________________________

#画像の挿入

img = Image.open('R.jfif')
st.image(img, use_column_width=0.5)

# __________________________________________________________________________

# 日経225銘柄を表示させる
filename = 'nikkei.csv'
df = pd.read_csv(filename, encoding='utf-8')

st.sidebar.write("""## <取得データの設定>""")
st.sidebar.write(""" 日経225銘柄一覧""")

st.sidebar.dataframe(df, 450, 175)

# __________________________________________________________________________

#データ作成
nikkei  =pd.read_csv('nikkei.csv')
companycode = dict(zip(nikkei['コード'], nikkei['社名']))

#sidebar1
st.write("""##   """) #行間調整
st.sidebar.write("""## ・株価チャート(ローソク足)""")

data_list = [k for k in companycode.keys()]
ticker = st.sidebar.selectbox('銘柄コードを選択してください', data_list)

end = st.sidebar.date_input("表示最終日を選択してください",)

st.sidebar.write("""##### ※直近10年間のうち、選択日より過去90日間のデータを表示します""")

#main
st.write("""##   """) #行間調整
st.write("""### ・株価チャート(ローソク足)""")
st.text('銘柄コード : {0} , 銘柄 : {1}'.format(ticker, companycode[ticker]))

#チャート作成
stock_code = '{0}.JP'.format(ticker)
data_source = 'stooq'

startday = end - timedelta(days=90)
start = datetime.strftime(startday, '%Y-%m-%d')
 
df = web.DataReader(stock_code, data_source=data_source, start=start, end=end)
df = df.sort_index()
date = df.index
x = np.arange(df.shape[0])
interval = 3
vals = np.arange(df.shape[0],step=interval)
labels = list(df[::interval].index.astype(str))


#グラフ1
fig = go.Figure(
    data=[go.Candlestick(x=x,open=df['Open'],high=df['High'],low=df['Low'],close=df['Close']),],
    layout=go.Layout(xaxis=dict(tickvals=vals,ticktext=labels,tickangle=-45))
    )

fig.update_layout(width=800, height=500)

config={'modeBarButtonsToAdd': ['drawline']}
st.plotly_chart(fig, use_container_width=True, config=config)

# __________________________________________________________________________

#sidebar2
st.sidebar.write("""## ・複数銘柄の株価推移比較""")

data_list2 = [k for k in companycode.keys()]
ticker2 = st.sidebar.selectbox('銘柄コード1',data_list2)

data_list3 = [k for k in companycode.keys()]
ticker3 = st.sidebar.selectbox('銘柄コード2',data_list3)

st.sidebar.write("""##### ※2020年１月から本日までのデータを表示します""")

#main2
st.write("""### ・複数銘柄の株価推移比較""")
st.text('銘柄1 : {0} , {1}'.format(ticker2, companycode[ticker2]))
st.text('銘柄2 : {0} , {1}'.format(ticker3, companycode[ticker3]))

#チャート作成
start2 = "2000-01-01"
dt = datetime.today()
end2 = dt.date()

stock_code1 = '{0}.JP'.format(ticker2)

df2 = web.DataReader(stock_code1, data_source=data_source, start=start2, end=end2)
df2 = df2.sort_index()
date2 = df2.index

stock_code2 = '{0}.JP'.format(ticker3)

df3 = web.DataReader(stock_code2, data_source=data_source, start=start2, end=end2)
df3 = df3.sort_index()
date3 = df3.index

#グラフ2

#Figureオブジェクト作成
fig = go.Figure()

#traceをFigureに追加
fig.add_traces(go.Scatter(x=date2, y=df2['Close'], name=ticker2, line=dict(color="#6B8C51")))
fig.add_traces(go.Scatter(x=date3, y=df3['Close'], name=ticker3, line=dict(color="#516B8C")))

#レイアウトの設定
fig.update_layout(width=800, height=500)

#軸の設定
fig.update_xaxes(title='日付')
fig.update_yaxes(title='終値')

st.plotly_chart(fig)

# __________________________________________________________________________

#　参考URL
# https://qiita.com/kyooooonaka/items/f543f2df5e7c86a5050d
# http://www.otupy.net/archives/39324598.html
