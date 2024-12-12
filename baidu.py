import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

class BaiduCrawler:
    def __init__(self):
        self.base_url = "https://www.baidu.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(urljoin(self.base_url, "/robots.txt"))
        self.robot_parser.read()
        self.results = []
        self.setup_gui()

    def setup_gui(self):
        # 创建主窗口
        self.root = Tk()
        self.root.title("百度搜索爬虫工具")
        self.root.geometry("800x600")

        # 创建搜索框和按钮
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(W, E, N, S))

        ttk.Label(frame, text="搜索关键词:").grid(row=0, column=0, padx=5)
        self.search_var = StringVar()
        self.search_entry = ttk.Entry(frame, textvariable=self.search_var, width=50)
        self.search_entry.grid(row=0, column=1, padx=5)

        ttk.Button(frame, text="搜索", command=self.search).grid(row=0, column=2, padx=5)

        # 创建结果显示区域
        self.result_text = Text(self.root, height=30, width=90)
        self.result_text.grid(row=1, column=0, padx=10, pady=10)

        # 创建导出按钮
        ttk.Button(self.root, text="导出到Excel", command=self.export_to_excel).grid(row=2, column=0, pady=10)

    def search(self):
        keyword = self.search_var.get()
        if not keyword:
            messagebox.showwarning("警告", "请输入搜索关键词！")
            return

        self.result_text.delete(1.0, END)
        self.results = []

        try:
            # 检查是否允许爬取
            if not self.robot_parser.can_fetch("*", self.base_url):
                messagebox.showerror("错误", "根据robots.txt规则，不允许爬取该网站！")
                return

            # 构建搜索URL
            search_url = f"{self.base_url}/s?wd={keyword}"
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()

            # 解析搜索结果
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='result')

            for idx, result in enumerate(search_results, 1):
                title = result.find('h3').get_text(strip=True) if result.find('h3') else "无标题"
                abstract = result.find('div', class_='c-abstract').get_text(strip=True) if result.find('div', class_='c-abstract') else "无描述"
                link = result.find('a').get('href') if result.find('a') else ""

                self.results.append({
                    '序号': idx,
                    '标题': title,
                    '描述': abstract,
                    '链接': link
                })

                # 显示在文本框中
                self.result_text.insert(END, f"序号: {idx}\n标题: {title}\n描述: {abstract}\n链接: {link}\n\n")

            messagebox.showinfo("提示", f"共找到 {len(self.results)} 条结果")

        except Exception as e:
            messagebox.showerror("错误", f"搜索出错：{str(e)}")

    def export_to_excel(self):
        if not self.results:
            messagebox.showwarning("警告", "没有可导出的搜索结果！")
            return

        try:
            # 创建输出目录
            output_dir = "搜索结果"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"搜索结果_{timestamp}.xlsx")

            # 创建DataFrame并导出到Excel
            df = pd.DataFrame(self.results)
            df.to_excel(filename, index=False)

            messagebox.showinfo("成功", f"结果已导出到：{filename}")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    crawler = BaiduCrawler()
    crawler.run()
