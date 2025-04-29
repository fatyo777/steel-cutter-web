import streamlit as st
from collections import defaultdict

st.set_page_config(page_title="鋼構配料工具 - 展翔好帥版 ver1.0", layout="centered")
st.title("鋼構配料工具 - 展翔好帥版 ver1.0")

stock_str = st.text_input("可用母料長度（逗號分隔）", "9000,10000,12000,12500,13000")
kerf = st.number_input("每段鋸損（mm）", value=0)
trim = st.number_input("每根去頭尾總長（mm）", value=0)

demand_input = st.text_area("成品長度與數量（每行一筆，例如：400 80）", "400 80\n520 46\n1200 62\n5880 32\n5660 78")

if st.button("開始配料"):
    try:
        stocks = list(map(int, stock_str.split(',')))
        usable_stocks = [s - trim for s in stocks]

        requests = []
        for line in demand_input.strip().split('\n'):
            if line.strip():
                l, q = map(int, line.strip().split())
                requests.extend([l] * q)

        requests.sort(reverse=True)
        result = []

        while requests:
            best_stock = None
            best_combo = []
            for stock, original in zip(usable_stocks, stocks):
                rem = stock
                combo = []
                for r in requests:
                    needed = r + kerf if combo else r
                    if needed <= rem:
                        combo.append(r)
                        rem -= needed
                if combo:
                    if not best_combo or len(combo) > len(best_combo):
                        best_combo = combo
                        best_stock = original

            if not best_combo:
                break
            for c in best_combo:
                requests.remove(c)
            result.append((best_stock, best_combo))

        summary = defaultdict(int)
        usage = defaultdict(int)
        lines = []
        for stock, combo in result:
            key = f"{stock} mm：" + ' + '.join(map(str, combo))
            summary[key] += 1
            usage[stock] += 1

        for k, v in summary.items():
            lines.append(f"{k}（共 {v} 支）")

        lines.append("\n母料長度用量統計：")
        for stock in sorted(usage):
            lines.append(f"{stock} mm：共使用 {usage[stock]} 支")

        st.text_area("配料結果：", value='\n'.join(lines), height=400)
    except Exception as e:
        st.error(f"錯誤：{e}")

st.markdown("---")
st.markdown("<div style='text-align: right; color: gray;'>展翔好帥版 ver1.0</div>", unsafe_allow_html=True)
