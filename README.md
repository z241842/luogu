| 这个作业属于哪个课程 | https://bbs.csdn.net/forums/fzusdn-0831 |
| ------ | ------ |
| 这个作业要求在哪里 | https://bbs.csdn.net/topics/617213407 |
| 这个作业的目标 | 熟练使用pyhton语言，学会requests请求，GUI设计，JSON解码，BeautifulSoup使用，使用copliot和ChatGPT写代码 |
| 学号 | 102102130 |
| github仓库 | https://github.com/z241842/z241842.github.io |
## 背景
为了更好地提升代码能力，jason哥想要收集相应的题目，有针对性地刷题。而需要收集洛谷所有题目，
但是工作量太大，所以jason哥急需大家运用爬虫技术，得到洛谷各种难度的题目和题解。
考虑到近来流行的AIGC技术，jason哥认为，在AI的帮助下，这项工作的难度会大大降低。

## 项目要求
在AIGC技术的帮助下，利用Copilot等工具，运用Python完成爬虫，
并用Tkinter库制作相应的GUI页面，将爬取到的题目以markdown文件存储，
放到相应文件夹下。

## 前端页面要求
页面上需要显示相应的输入框以便筛选相应的题目。
![img](https://img-community.csdnimg.cn/images/a106e341c2494de886ee6ad6c0b0e59f.png "#left")
筛选条件如上，包含题目难度，包括暂无评定入门，普及-，普及/提高-，普及+/提高，提高+/省选-，省选/NOI-，
NOI/NOI+/CTSC，和一些其他关键词，如算法/来源/标题/题目编号等。

## 爬取内容存放要求
爬下所有显示的题目：

对于每一道题，以markdown格式存储，命名为“题目编号-标题.md”，对应题目的第一篇题解，
以markdown格式存储，命名为“题目编号-标题-题解.md”，一起放入文件夹”题目编号-标题“下。

对于爬取的所有题目，将其”题目编号-标题“文件夹放到“题目难度-关键词”的目录下，若搜索时存在多个关键词，
以“关键词1-关键词2-…”展示。

## 结合AIGC
现有的AIGC应用包括VScode中的Copilot插件，Cursor IDE等等，请安装并利用这些工具辅助完成代码，要求
完成一张表格，包含以下内容：

1. 爬虫任务可以被分解成哪几个小任务？
2. 预估哪几个子任务可以利用AIGC？
3. 实际中哪些部分利用了AIGC？
4. AIGC技术的优缺点，适合用在哪些方面，不适合实现哪些功能？

### AIGC表格


| 子任务 | 预估哪些部分使用AIGC | 实际中哪些部分使用AIGC |
| ------ | ------ | ------ |
| 爬取题目 | 伪装heards，发送请求获取源码 | 使用AIGC |
| 爬取题解 | 定位题目题解，获取网页源码，解码 | 自行解码 |
| 爬取标签和难度 | 定位题目标签和难度，获取网页源码 | 自行编码 |
| 存储和搜索 | 设置窗口大小，按键文本框逻辑 | 自行编码 | 
| GUI设计 | 设置窗口大小，组件布局 | 使用AIGC  |

## PSP表格


| psps | 预估耗时/分钟 | 实际耗时/分钟 |
| ------ | ------ | ------ |
| 计划 | 50 | 30 |
| 准备 | 200 | 240 |
| 设计 | 120 | 150 |
| 编码 | 240 | 300 |
| 测试、修改 | 240 | 320 |
| 总结 | 30 | 20 |
| 合计 | 880 | 1060 | 




## 前端
首页

![img](https://img-community.csdnimg.cn/images/f31758c149a04449aafe01da4928f9a5.png "#left")

爬题

![img](https://img-community.csdnimg.cn/images/8b199346c42f42e39cedb950a7433168.png "#left")


## 代码
前置函数

```python
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
    '__client_id': '2a85a842dc5ec79157e99bb9ff1c722cb27c38e1',
    '_uid': '830471'
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


# 定义提交函数
def submit(fuction):
    # 获取参数
    # difficulty = DIFFICULTIES[difficulty_var.get()]
    # algorithm = algorithm_entry.get()
    title = title_entry.get()

    # 调用后端函数
    # crawl(difficulty, algorithm, title)
    # getProblemList(title)
    fuction(title)


# 界面切换函数
def show_page(page):
    for p in pages:
        p.pack_forget()
    page.pack()


```
爬取题目
```python
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
        cfilename = './题目/P' + problem + '.md'
        with open(cfilename, "w", encoding="utf-8") as file:
            file.write(md)
        output_text.insert(tk.END, "P" + problem + "......题目爬取成功" + "\n")
    except Exception as err:
        output_text.insert(tk.END, str(err) + "\n")


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

```
爬取题解

```python
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
        cfilename = './题解/P' + problem + '.md'
        with open(cfilename, "w", encoding="utf-8") as file:
            file.write(md)
        output_text.insert(tk.END, "P" + problem + "......题解爬取成功" + "\n")
    except Exception as err:
        output_text.insert(tk.END, str(err) + "\n")


def check_solution():
    start = start_entry.get()
    end = end_entry.get()

    pattern = r'[1-9][0-9]{3,3}'
    base_url = "https://www.luogu.com.cn/problem/solution/P"

    if re.match(pattern, start) and re.match(pattern, end):
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "正在爬取，请稍后\n")
        startI = int(start)
        endI = int(end)
        probleList = []
        for i in range(startI, endI + 1):
            probleList.append(str(i))
        for problem in probleList:
            crawl_solution(problem, base_url)
    else:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "数据不合法，请检查你的输入数据\n")

```
GUI设计

```python
if __name__ == '__main__':
    root = tk.Tk()
    root.title("洛谷爬题工具")

    # 创建搜题界面
    page1 = tk.Frame(root)
    difficulty_label = tk.Label(page1, text="题目难度")
    difficulty_label.pack(side=tk.LEFT)
    difficulty_var = tk.StringVar(value="入门")
    difficulty_choices = ["入门", "普及-", "普及/提高-", "普及+/提高", "提高+/省选-", "省选/NOI-",
                          "NOI/NOI+/CTSC"]
    difficulty_dropdown = tk.OptionMenu(page1, difficulty_var, *difficulty_choices)
    difficulty_dropdown.pack(side=tk.LEFT)
    # 创建两个输入框
    algorithm_label = tk.Label(page1, text="算法/来源")
    algorithm_label.pack(side=tk.LEFT)
    algorithm_entry = tk.Entry(page1)
    algorithm_entry.pack(side=tk.LEFT)
    title_label = tk.Label(page1, text="标题/题目编号")
    title_label.pack(side=tk.LEFT)
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
    submit_button = tk.Button(page1, text="提交", command=lambda: submit(getProblemList))
    submit_button.pack(side=tk.LEFT)
    # 创建返回主页按钮
    button1 = tk.Button(page1, text="返回主界面", command=lambda: show_page(main_page))
    button1.pack()

    # 创建主界面
    main_page = tk.Frame(root)
    label_main = tk.Label(main_page, text="洛谷爬题主页")
    label_main.pack()
    button_page1 = tk.Button(main_page, text="搜题", command=lambda: show_page(page1))
    button_page1.pack()

    # 创建三个子界面
    page2 = tk.Frame(root)
    label1 = tk.Label(page2, text="爬取题目与题解")
    label1.pack()
    start_label = tk.Label(page2, text="爬取的起始题目")
    start_label.pack()
    start_entry = tk.Entry(page2)
    start_entry.pack()
    end_label = tk.Label(page2, text="爬取的终止题目")
    end_label.pack()
    end_entry = tk.Entry(page2)
    end_entry.pack()
    crawl_button1 = tk.Button(page2, text="爬取题目", command=crawl_data)
    crawl_button1.pack()
    crawl_button2 = tk.Button(page2, text="爬取题解", command=crawl_dataSolu)
    crawl_button2.pack()
    output_text = tk.Text(page2, height=3, width=40)
    output_text.pack()
    back_button = tk.Button(page2, text="返回主界面", command=lambda: show_page(main_page))
    back_button.pack()
    # stop_button = tk.Button(page2, text="中止爬取", command=executor.shutdown) # 添加一个中止按钮
    # stop_button.pack()
    button_page2 = tk.Button(main_page, text="爬题", command=lambda: show_page(page2))
    button_page2.pack()

    # 初始显示主界面
    pages = [main_page, page1, page2]
    show_page(main_page)

    root.mainloop()


```

## 测试
### 爬取题目

![img](https://img-community.csdnimg.cn/images/760da18ac6324ded96e531dc74fe68a0.png "#left")

存储

![img](https://img-community.csdnimg.cn/images/e36c42ab62c9475ea000c2fd114323d1.png "#left")

查看

![img](https://img-community.csdnimg.cn/images/ddcdee84277b47cc88f560b75bab2cef.png "#left")

### 爬取题解

![img](https://img-community.csdnimg.cn/images/a3a3817dfa3741f4a222be845c791693.png "#left")

存储

![img](https://img-community.csdnimg.cn/images/51b7bf4d70804238b1053fe6cea0e08a.png "#left")

查看

![img](https://img-community.csdnimg.cn/images/50ce829a6b5e438ca0cf601cddaad122.png "#left")

### 搜题

![img](https://img-community.csdnimg.cn/images/e5e2d00c0b16449f88f2c5c328797741.png "#left")



## 心得体会
从本次作业中，我加深了对python爬虫的了解，熟悉了copilot和AIGC的运用，能够利用tkinter设计GUI。
我的不足之处：缺乏实践经验，编写代码不能熟练，对项目设计的了解还停留在较浅的层次；对代码布局的把控还有待改善，对AI的使用还不够熟练，将问题复述给AI时还有一定的难度。
