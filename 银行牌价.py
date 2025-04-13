import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="中国银行汇率比价", page_icon="💱", layout="centered")
st.title("💱 中国各大银行实时美元汇率比价")
st.caption("数据来源：[https://www.huilv.cc](https://www.huilv.cc)，每10分钟自动更新")

@st.cache_data(ttl=600)
def get_usd_rates():
    url = "https://www.huilv.cc/bank/usd/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.select_one("table.data")
    if not table:
        st.error("❌ 无法获取数据，网站结构可能已经更改。")
        return pd.DataFrame()

    rows = table.find_all("tr")[1:]
    data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            try:
                bank = cols[0].text.strip()
                buy = float(cols[1].text.strip())
                sell = float(cols[2].text.strip())
                time = cols[4].text.strip()
                data.append({
                    "银行": bank,
                    "结汇价 (买入)": buy,
                    "购汇价 (卖出)": sell,
                    "更新时间": time
                })
            except:
                continue

    return pd.DataFrame(data)

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
    st.markdown("👑 表示当前最优结汇/购汇价格")
else:
    st.warning("暂无可展示的数据，请稍后刷新。")
