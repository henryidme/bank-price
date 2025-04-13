import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="中国银行汇率比价", page_icon="💱", layout="centered")
st.title("💱 中国银行实时美元汇率")
st.caption("数据来源：[中国银行外汇牌价](https://srh.bankofchina.com/search/whpj/search_cn.jsp)")

@st.cache_data(ttl=600)
def get_usd_rates():
    url = "https://srh.bankofchina.com/search/whpj/search_cn.jsp"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find("table", attrs={"align": "center"})
    if not table:
        st.error("无法找到汇率表格，网站结构可能已更改。")
        return pd.DataFrame()

    rows = table.find_all("tr")[1:]
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 8:
            currency = cols[0].text.strip()
            if currency == "美元":
                try:
                    buy = float(cols[1].text.strip())
                    sell = float(cols[3].text.strip())
                    time = cols[7].text.strip()
                    data.append({
                        "币种": currency,
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
    st.markdown("👑 表示当前最优结汇/购汇价格。数据每10分钟自动刷新。")
else:
    st.warning("暂无可展示的数据，请稍后刷新。")
