import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Selector Web", layout="wide")

st.title("📈 股票策略多功能平台")
mode = st.sidebar.radio("选择功能模式", [
    "行情适配（实时）",
    "三维共振（收盘筛选）",
    "三维共振（近3月回测）"
])

# ---------- 工具函数 ----------
def load_csv(file):
    try:
        return pd.read_csv(file)
    except:
        return pd.read_excel(file)

def strategy_three_dim(df):
    """三维共振策略核心逻辑"""
    cond1 = df['close'] > df['ma5']
    cond2 = df['close'] > df['ma10']
    cond3 = df['close'] > df['ma20']
    cond4 = df['volume'] > df['volume'].rolling(5).mean()
    return df[cond1 & cond2 & cond3 & cond4]

# ---------- 模式 1：行情适配（实时） ----------
if mode == "行情适配（实时）":
    st.subheader("📊 行情适配策略 - 实时版")
    uploaded_file = st.file_uploader("上传实时行情CSV/Excel", type=["csv", "xlsx"])
    if uploaded_file:
        df = load_csv(uploaded_file)
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        result = strategy_three_dim(df)
        st.write(f"选出 {len(result)} 只股票：")
        st.dataframe(result)
        st.download_button("下载结果 CSV", result.to_csv(index=False), "result.csv")

# ---------- 模式 2：三维共振（收盘筛选） ----------
elif mode == "三维共振（收盘筛选）":
    st.subheader("📌 三维共振策略 - 收盘后筛选")
    uploaded_file = st.file_uploader("上传收盘数据 CSV/Excel", type=["csv", "xlsx"])
    if uploaded_file:
        df = load_csv(uploaded_file)
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        result = strategy_three_dim(df)
        st.write(f"符合条件的股票数量: {len(result)}")
        st.dataframe(result)
        st.download_button("下载结果 CSV", result.to_csv(index=False), "close_select.csv")

# ---------- 模式 3：三维共振（近3月回测） ----------
elif mode == "三维共振（近3月回测）":
    st.subheader("🕒 三维共振策略 - 近3个月回测")
    uploaded_file = st.file_uploader("上传历史数据 CSV/Excel", type=["csv", "xlsx"])
    if uploaded_file:
        df = load_csv(uploaded_file)
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'] >= datetime.now() - timedelta(days=90)]
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        trade_log = []
        for date in sorted(df['date'].unique()):
            daily_data = df[df['date'] == date]
            selected = strategy_three_dim(daily_data)
            for _, row in selected.iterrows():
                trade_log.append({
                    "date": date,
                    "code": row['code'],
                    "close": row['close']
                })
        trade_df = pd.DataFrame(trade_log)
        st.write(f"回测选出 {len(trade_df)} 条交易信号")
        st.dataframe(trade_df)
        st.download_button("下载回测结果 CSV", trade_df.to_csv(index=False), "backtest.csv")
