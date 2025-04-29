import streamlit as st
from collections import defaultdict, Counter

def simplify_combo(combo):
    count = Counter(combo)
    parts = []
    for length in sorted(count.keys(), reverse=True):
        qty = count[length]
        if qty > 1:
            parts.append(f"{length}*{qty}")
        else:
            parts.append(f"{length}")
    return ' + '.join(parts)

st.set_page_config(page_title="配料工具 - 展翔好帥版 ver1.0")
st.title("配料工具 - 展翔好帥版 ver1.0")

stock_str = st.text_input("可用母料長度（逗號分隔）", "")
kerf = st.number_input("每段鋸損 (mm)", value=0)
trim = st.number_input("每根去頭尾總長 (mm)", value=0)
demand_input = st.text_area("成品長度與數量（每行一筆，例如：400 80）", "")

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
                remaining = stock
                combo = []
                for r in requests:
                    needed = r + (kerf if combo else 0)
                    if needed <= remaining:
                        combo.append(r)
                        remaining -= needed
                if combo:
                    if not best_combo or len(combo) > len(best_combo):
                        best_combo = combo
                        best_stock = original
            if not best_combo:
                break
            for item in best_combo:
                requests.remove(item)
            result.append((best_stock, best_combo))

        summary = defaultdict(list)
        for stock, combo in result:
            summary[stock].append(combo)

        usage_counter = Counter()
        total_all_loss = 0
        grouped_output = defaultdict(int)
        output_lines = []

        for stock, combos in sorted(summary.items(), reverse=True):
            for combo in combos:
                simplified = simplify_combo(combo)
                total_used = sum(combo) + (len(combo) - 1) * kerf
                remain_loss = stock - total_used - trim
                grouped_output[(stock, simplified, remain_loss)] += 1
                usage_counter[stock] += 1
                total_all_loss += remain_loss + trim

        for (stock, simplified, remain), count in grouped_output.items():
            output_lines.append(f"{stock} mm：{simplified}（x {count}支）[每支剩餘 {remain}mm，共 {remain * count}mm]")

        output_lines.append("\n母料長度用量統計：")
        for stock in sorted(usage_counter.keys()):
            output_lines.append(f"{stock} mm：共使用 {usage_counter[stock]} 支")

        output_lines.append("\n總損料統計：")
        output_lines.append(f"{total_all_loss} mm")

        st.text_area("配料結果", value="\n".join(output_lines), height=500)

    except Exception as e:
        st.error(f"錯誤：{e}")

st.markdown("---")
st.markdown("<div style='text-align: right; color: gray;'>配料工具 - 展翔好帥版 ver1.0</div>", unsafe_allow_html=True)
