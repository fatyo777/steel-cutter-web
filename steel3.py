# 鋼構配料工具 - 展翔好帥版 ver1.0（支援中文 PDF 匯出）

import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from collections import defaultdict
import os
from fpdf import FPDF
import pandas as pd

# PDF 中文字型路徑（Windows 正黑體）
FONT_PATH = "C:/Windows/Fonts/msjh.ttc"

def calculate():
    try:
        stocks = list(map(int, stock_entry.get().split(',')))
        kerf = int(kerf_entry.get()) if kerf_entry.get().strip() else 0
        trim = int(trim_entry.get()) if trim_entry.get().strip() else 0
        usable_stocks = [s - trim for s in stocks]

        requests = []
        for line in demand_text.get("1.0", tk.END).strip().split('\n'):
            if not line.strip():
                continue
            length, qty = map(int, line.strip().split())
            requests.extend([length] * qty)

        requests.sort(reverse=True)
        result = []

        while requests:
            best_stock = None
            best_combination = []
            for stock, original_stock in zip(usable_stocks, stocks):
                remaining = stock
                combo = []
                for r in requests:
                    needed = r + kerf if combo else r
                    if needed <= remaining:
                        combo.append(r)
                        remaining -= needed
                if combo:
                    if not best_combination or len(combo) > len(best_combination):
                        best_combination = combo
                        best_stock = original_stock

            if not best_combination:
                break

            for item in best_combination:
                requests.remove(item)
            result.append((best_stock, best_combination))

        output.delete("1.0", tk.END)

        summary = {}
        stock_usage = defaultdict(int)
        for stock, combo in result:
            key = f"{stock} mm：" + ' + '.join(map(str, combo))
            summary[key] = summary.get(key, 0) + 1
            stock_usage[stock] += 1

        lines = []
        for k, v in summary.items():
            line = f"{k}（共 {v} 支）"
            output.insert(tk.END, line + "\n")
            lines.append(line)

        output.insert(tk.END, "\n母料長度用量統計：\n")
        lines.append("")
        lines.append("母料長度用量統計：")
        for stock in sorted(stock_usage):
            line = f"{stock} mm：共使用 {stock_usage[stock]} 支"
            output.insert(tk.END, line + "\n")
            lines.append(line)

        global latest_result_lines
        latest_result_lines = lines

    except Exception as e:
        messagebox.showerror("錯誤", str(e))

def export_pdf():
    if not latest_result_lines:
        messagebox.showwarning("提示", "沒有可匯出的資料")
        return
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("msjh", "", FONT_PATH, uni=True)
        pdf.set_font("msjh", size=12)

        for line in latest_result_lines:
            pdf.cell(0, 10, txt=line, ln=True)

        pdf.set_xy(170, 280)
        pdf.set_font("msjh", size=10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(30, 10, txt="展翔好帥版 ver1.0")

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")]
        )
        if filepath:
            pdf.output(filepath)
            messagebox.showinfo("成功", f"PDF 匯出成功！\n路徑：{filepath}")
    except Exception as e:
        messagebox.showerror("匯出失敗", str(e))

def export_excel():
    if not latest_result_lines:
        return
    try:
        rows = [line for line in latest_result_lines if '（共' in line or '共使用' in line]
        df = pd.DataFrame(rows, columns=['配料結果'])
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if filepath:
            df.to_excel(filepath, index=False)
            messagebox.showinfo("成功", f"Excel 匯出成功！\n路徑：{filepath}")
    except Exception as e:
        messagebox.showerror("匯出失敗", str(e))

latest_result_lines = []

root = tk.Tk()
root.title("鋼構配料工具 - 展翔好帥版 ver1.0")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

stock_label = tk.Label(frame, text="可用母料長度（用逗號分隔）：")
stock_label.grid(row=0, column=0, sticky="w")
stock_entry = tk.Entry(frame, width=50)
stock_entry.grid(row=1, column=0)

kerf_label = tk.Label(frame, text="每段鋸損 mm（例如 3）：")
kerf_label.grid(row=2, column=0, sticky="w")
kerf_entry = tk.Entry(frame, width=10)
kerf_entry.grid(row=3, column=0, sticky="w")

trim_label = tk.Label(frame, text="每根去頭尾總長 mm（例如 40）：")
trim_label.grid(row=2, column=1, sticky="w")
trim_entry = tk.Entry(frame, width=10)
trim_entry.grid(row=3, column=1, sticky="w")

demand_label = tk.Label(frame, text="成品長度與數量（每行一筆，格式如：400 80）：")
demand_label.grid(row=4, column=0, sticky="w")
demand_text = scrolledtext.ScrolledText(frame, width=50, height=8)
demand_text.grid(row=5, column=0, columnspan=2)

calc_btn = tk.Button(frame, text="開始配料", command=calculate)
calc_btn.grid(row=6, column=0, pady=10)

export_pdf_btn = tk.Button(frame, text="匯出 PDF", command=export_pdf)
export_pdf_btn.grid(row=6, column=1)

export_excel_btn = tk.Button(frame, text="匯出 Excel", command=export_excel)
export_excel_btn.grid(row=6, column=2)

output = scrolledtext.ScrolledText(frame, width=65, height=25)
output.grid(row=7, column=0, columnspan=3)

version_label = tk.Label(root, text="展翔好帥版 ver1.0", fg="gray")
version_label.pack(anchor="se", padx=10, pady=5)

root.mainloop()
