import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="中国各大银行实时汇率比价", page_icon="💱", layout="centered")
st.title("💱 中国主要银行实时汇率比价")
st.caption("数据来源：[汇率网](https://www.huilv.cc/), 币种：美元 USD")


@st.cache_data(ttl=600)  # 每10分钟缓存刷新
def get_usd_rates():
    url = "https://www.huilv.cc/bank/usd/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find("table", class_="data")
    rows = table.find_all("tr")[1:]

    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            bank = cols[0].text.strip()
            buy = cols[1].text.strip()
            sell = cols[2].text.strip()
            time = cols[4].text.strip()
            data.append({
                "银行": bank,
                "结汇价 (买入)": float(buy) if buy != '-' else None,
                "购汇价 (卖出)": float(sell) if sell != '-' else None,
                "更新时间": time
            })

    df = pd.DataFrame(data).dropna()
    return df


def add_crowns(df):
    df = df.copy()
    best_buy = df['结汇价 (买入)'].max()
    best_sell = df['购汇价 (卖出)'].min()

    df['结汇价 (买入)'] = df['结汇价 (买入)'].apply(
        lambda x: f"{x:.4f} 👑" if x == best_buy else f"{x:.4f}")
    df['购汇价 (卖出)'] = df['购汇价 (卖出)'].apply(
        lambda x: f"{x:.4f} 👑" if x == best_sell else f"{x:.4f}")
    return df


df = get_usd_rates()
df_display = add_crowns(df)

st.dataframe(df_display, use_container_width=True)
st.markdown("👑 表示当前最优结汇价或购汇价。数据每10分钟自动刷新。")
