#  ___coding=UTF-8___

from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import pandas as pd
from queue import Queue
import threading
import os

path = '/Users/stone/Desktop/'  # 可根据实际情况调整文件存储位置。
indexname = 'index_file.xlsx'   # 章节列表，可供备查。
filename = '23123.txt'          # 文件名称，可随意更改。

Meta_Url = 'https://www.xbiquwx.la/12_12583/'     # 小说网址
con_url = 'https://www.xbiquwx.la/12_12583/{}'    # 章节网址模板

cpt_urls = []
cpt_name = []
wrong_list = []

thread_count = 5     # 创建5个线程


class DownloadThread(threading.Thread):
    def __init__(self, queue: Queue):
        super().__init__(daemon=True)
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            cpt_job = self.queue.get()
            cpt_url = con_url.format(cpt_job[1])
            tmp_name = str(cpt_job[0])

            cpt_re = requests.get(cpt_url, headers={'User-Agent': UserAgent().random}, timeout=30)
            cpt_soup = BeautifulSoup(cpt_re.content, 'lxml')
            cpt_con = cpt_soup.find(id='content').text.split()
            cpt_head = cpt_soup.find(class_='bookname').find('h1').text

            with open('files/{}.txt'.format(tmp_name), 'a', encoding='UTF-8') as f:
                f.write(cpt_head)  # 插入章节名称
                f.write('\r\n')  # 插入空行
                for i in cpt_con:
                    f.write(i)  # 插入段落
                    f.write('\r\n')  # 插入空行


def lists_get(url):  # 获取所有章节链接，并保存为Excel
    soup = BeautifulSoup(requests.get(url, headers={'User-Agent': UserAgent().random}, timeout=30).content, "lxml")
    li_list = soup.find(id='list').select('dd')  # 小说目录章节及网址
    for li in li_list:
        cpt_urls.append(li.a['href'])
        cpt_name.append(li.text)

    data = {
        'nameline': cpt_name,
        'urlline': cpt_urls
    }

    df = pd.DataFrame(data)

    writer = pd.ExcelWriter(path + indexname)
    df.to_excel(writer, float_format='%.5f')

    writer.save()
    print('目录文件保存成功,准备下载')


def cpt_queue():     # 创建队列，安排链接入组
    df = pd.read_excel(path + indexname)
    urllists = df['urlline']
    q = Queue()
    for i in range(len(urllists)):
        cpt_url = urllists[i]
        q.put([i, cpt_url])

    return q


def create_threading(queue):     # 创建线程
    thread_list = []
    for i in range(thread_count):
        thread = DownloadThread(queue)
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()


def composite_file():    # 合并文件
    with open(path + filename, 'a') as f:  #
        for i in range(len(os.listdir('files'))):
            with open('files/{}.txt'.format(i), 'r') as bytes_f:
                f.write(bytes_f.read())

    for i in os.listdir('files'):  # 清理临时文件
        os.remove('files/{}'.format(i))


def main():
    lists_get(Meta_Url)
    queue = cpt_queue()
    create_threading(queue)
    composite_file()


if __name__ == '__main__':
    main()
