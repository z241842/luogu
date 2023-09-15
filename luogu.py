import json
import tkinter as tk
import threading
import re
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
import jieba
from tkinter import scrolledtext
from urllib import parse
import ujson
import concurrent.futures

# 创建一个全局标志变量，用于通知线程是否终止
stop_threads = False
cookies = {
    '__client_id': 'b43680425b0784c23492eb0166755ed68264fb0f',
    "login_referer": "https://www.luogu.com.cn/auth/login",
    '_uid': '1090228',
    "C3VK": "ae16e2"
}


def HTMLAuth(url):
    # 创建一个随机User-Agent生成器
    user_agent = UserAgent()

    # 设置请求头
    headers = {
        'User-Agent': user_agent.random,
    }
    # 'Referer': 'https://www.luogu.com.cn/auth/login',  # 设置Referer字段，模拟从某个页面跳转过来

    # 创建一个会话对象
    session = requests.Session()
    for key in cookies:
        session.cookies[key] = cookies[key]

    response = session.get(url=url, headers=headers)

    # 检查是否登录成功
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")

    # 关闭会话
    session.close()
    return response.text


def HTML(url):
    # 创建一个随机User-Agent生成器
    user_agent = UserAgent()

    # 设置请求头
    headers = {
        'User-Agent': user_agent.random,
    }
    response = requests.get(url, headers=headers)
    # 继续处理响应内容
    return response.text


def show_frame(frame):
    frame.tkraise()


def getProblemList(title='P1000', difficulties='入门', algrithm=''):
    url = "https://www.luogu.com.cn/problem/list"
    response = HTML(url=url)
    soup = BeautifulSoup(response, "lxml")

    table = soup.select("div[class='lg-container'] ul li a")
    for row in table:
        id = row['href']
        title_text = str(row.text)
        title_list = jieba.lcut(title_text)
        # print(title_list)
        id = str(id)
        title_list.append(id)
        if title in title_list:
            # print(title_text)
            text.insert(tk.END, id + "   " + title_text + "\n")


# 提交函数
def submit(fuction):
    # 获取参数
    # difficulty = DIFFICULTIES[difficulty_var.get()]
    # algorithm = algorithm_entry.get()
    title = title_entry.get()

    # 调用后端函数
    # crawl(difficulty, algorithm, title)
    # getProblemList(title)
    fuction(title)


# 翻页
def show_page(page):
    for p in pages:
        p.pack_forget()
    page.pack()


# 爬取题目
def crawl_problem(problem, base_url):
    try:
        url = base_url + problem
        html = HTML(url=url)
        bs = BeautifulSoup(html, "lxml")
        core = bs.select("article")[0]
        md = str(core)
        md = re.sub("<h1>", "# ", md)
        md = re.sub("<h2>", "## ", md)
        md = re.sub("<h3>", "#### ", md)
        md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
        cfilename = 'C:\\Users\\zmk\\洛谷习题\\problems' + problem + '.md'
        with open(cfilename, "w", encoding="utf-8") as file:
            file.write(md)
        output_text.insert(tk.END, "P" + problem + "......题目爬取成功" + "\n")
    except Exception as err:
        output_text.insert(tk.END, str(err) + "\n")


# 爬取题解
def crawl_solution(problem, base_url):
    try:
        url = base_url + problem
        html = HTMLAuth(url=url)
        bs = BeautifulSoup(html, "lxml")
        js_code = bs.find("script").get_text()
        result1 = re.search(r"window._feInjection = JSON.parse\(decodeURIComponent\(\"(.*)\"\)\)", js_code).group(0)
        result2 = re.search(r"(?<=window._feInjection = JSON.parse\(decodeURIComponent\(\").*(?=\"\)\))",
                            result1).group(0)
        python_code = parse.unquote(result2)
        json_file = json.loads(python_code)
        solution = json_file["currentData"]["solutions"]["result"]
        md = solution[0]["content"]
        cfilename = 'C:\\Users\\zmk\\洛谷习题\\solutions' + problem + '.md'
        with open(cfilename, "w", encoding="utf-8") as file:
            file.write(md)
        output_text.insert(tk.END, "P" + problem + "......题解爬取成功" + "\n")
    except Exception as err:
        output_text.insert(tk.END, str(err) + "\n")


# 题目爬取界面数据检查函数
def check_problem():
    start = start_entry.get()
    end = end_entry.get()

    pattern = r'[1-9][0-9]{3,3}'
    base_url = "https://www.luogu.com.cn/problem/P"

    if re.match(pattern, start) and re.match(pattern, end):
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "正在爬取，请稍后\n")
        startI = int(start)
        endI = int(end)
        probleList = []
        for i in range(startI, endI + 1):
            probleList.append(str(i))
        for problem in probleList:
            crawl_problem(problem, base_url)
    else:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "数据不合法，请检查你的输入数据\n")




# GUI设计
if __name__ == '__main__':
    root = tk.Tk()
    root.title("洛谷爬题工具")
    root.geometry("1000x370")

    # 创建搜题界面
    page1 = tk.Frame(root)
    difficulty_label = tk.Label(page1, text="筛选条件", font="宋体 15 bold italic")
    difficulty_label.place(x=110, y=50)
    difficulty_label = tk.Label(page1, text="题目难度",font="宋体 15 bold italic")
    difficulty_label.place(x=50,y=100)
    difficulty_var = tk.StringVar(value="入门")
    difficulty_choices = ["入门", "普及-", "普及/提高-", "普及+/提高", "提高+/省选-", "省选/NOI-",
                          "NOI/NOI+/CTSC"]
    difficulty_dropdown = tk.OptionMenu(page1, difficulty_var, *difficulty_choices)
    difficulty_dropdown.place(x=145,y=95)
    # 创建两个输入框
    algorithm_label = tk.Label(page1, text="算法/来源/时间/状态",font="宋体 10 bold italic")
    algorithm_label.place(x=0,y=140)
    algorithm_entry = tk.Entry(page1)
    algorithm_entry.pack(side=tk.LEFT)
    title_label = tk.Label(page1, text="标题/题目编号",font="宋体 10 bold italic")
    title_label.place(x=170,y=140)
    title_entry = tk.Entry(page1)
    title_entry.pack(side=tk.LEFT)
    # 创建一个输出框
    # 创建滚动条
    scrollbar = tk.Scrollbar(page1)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    # 创建文本框并与滚动条关联
    text = scrolledtext.ScrolledText(page1, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    # 将滚动条与文本框关联
    scrollbar.config(command=text.yview)
    # 创建提交按钮
    submit_button = tk.Button(page1, text="提交", command=lambda: submit(getProblemList),font="宋体 15 bold italic")
    submit_button.place(x=220,y=200)
    # 创建返回主页按钮
    button1 = tk.Button(page1, text="返回主界面", command=lambda: show_page(main_page),font="宋体 15 bold italic")
    button1.pack(side=tk.RIGHT)

    # 创建主界面
    main_page = tk.Frame(root)
    label_main = tk.Label(main_page, text="欢迎使用洛谷爬虫工具！",font="宋体 20 bold italic")
    label_main.pack(fill="y",ipady=50)
    button_page1 = tk.Button(main_page, text="搜题", command=lambda: show_page(page1), width=10,height=5,font="宋体 15 bold italic")
    button_page1.pack(side=tk.LEFT,fill="y")

    # 创建三个子界面
    page2 = tk.Frame(root)
    label1 = tk.Label(page2, text="爬取题目与题解",font="宋体 15 bold italic")
    label1.place(x=450,y=250)
    start_label = tk.Label(page2, text="爬取的起始题目",font="宋体 15 bold italic")
    start_label.pack()
    start_entry = tk.Entry(page2)
    start_entry.pack()
    end_label = tk.Label(page2, text="爬取的终止题目",font="宋体 15 bold italic")
    end_label.pack()
    end_entry = tk.Entry(page2)
    end_entry.pack()
    crawl_button1 = tk.Button(page2, text="爬取题目", command=check_problem,font="宋体 15 bold italic")
    crawl_button1.pack()
    crawl_button2 = tk.Button(page2, text="爬取题解", command=check_solution,font="宋体 15 bold italic")
    crawl_button2.pack()
    output_text = tk.Text(page2, height=10, width=40)
    output_text.pack()
    back_button = tk.Button(page2, text="返回主界面", command=lambda: show_page(main_page),font="宋体 15 bold italic")
    back_button.pack()
    button_page2 = tk.Button(main_page, text="爬题", command=lambda: show_page(page2), width=10,height=5,font="宋体 15 bold italic")
    button_page2.pack(side=tk.RIGHT)

    # 初始显示主界面
    pages = [main_page, page1, page2]
    show_page(main_page)

    root.mainloop()
