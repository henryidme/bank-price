import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="中国银行汇率比价", page_icon="💱", layout="centered")
st.title("💱 中国银行实时美元汇率")
st.caption("数据来源：[中国银行外汇牌价](https://srh.bankofchina.com/search/whpj/search_cn.jsp)")

@st.cache_data(ttl=600)
def get_usd_rates():
    url = "https://srh.bankofchina.com/search/whpj/search_cn.jsp"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    
    # 获取页面中的JSON数据
    json_data = r.text.split('var exchangeJsonData = ')[1].split(';\n')[0]
    data = json.loads(json_data)

    usd_data = []
    for item in data:
        if item['currency'] == '美元':
            usd_data.append({
                "币种": item['currency'],
                "结汇价 (买入)": float(item['buy']),
                "购汇价 (卖出)": float(item['sell']),
                "更新时间": item['time']
            })
    
    return pd.DataFrame(usd_data)

def add_crowns(df):
    df = df.copy()
    if df.empty:
        return df

    best_buy = df['结汇价 (买入)'].max()
    best_sell = df['购汇价 (卖出)'].min()

    df['结汇价 (买入)'] = df['结汇价 (买入)'].apply(
        lambda x: f"{x:.4f} 👑" if x == best_buy else f"{x:.4f}")
    df['购汇价 (卖出)'] = df['购汇价 (卖出)'].apply(
        lambda x: f"{x:.4f} 👑" if x == best_sell else f"{x:.4f}")
    return df

df = get_usd_rates()
if not df.empty:
    df_display = add_crowns(df)
    st.dataframe(df_display, use_container_width=True)
    st.markdown("👑 表示当前最优结汇/购汇价格。数据每10分钟自动刷新。")
else:
    st.warning("暂无可展示的数据，请稍后刷新。")
