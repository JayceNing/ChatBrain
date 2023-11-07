import argparse
import base64
import configparser
import datetime
import io
import json
import os
import re
from collections import namedtuple
import glob
import shutil

# import arxiv
import fitz
import numpy as np
import openai
# 导入所需的库
import requests
import tenacity
import tiktoken
from bs4 import BeautifulSoup
from PIL import Image

from collections import defaultdict

import uvicorn
from fastapi import Body, FastAPI, File, Form, Query, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from SparkApi_none_stream import create as SparkCreate

OPENAI_API_KEY = "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"

ArxivParams = namedtuple(
    "ArxivParams",
    [
        "query",
        "key_word",
        "page_num",
        "max_results",
        "days",
        "sort",
        "save_image",
        "file_format",
        "language",
    ],
)


class Paper:
    def __init__(self, path, date='', title='', url='', abs='', authers=[]):
        # 初始化函数，根据pdf路径初始化Paper对象                
        self.url = url  # 文章链接
        self.path = path  # pdf路径
        self.date = date  # 发布时间
        self.section_names = []  # 段落标题
        self.section_texts = {}  # 段落内容
        self.abs = abs
        self.title_page = 0
        self.title = title
        self.pdf = fitz.open(self.path)  # pdf文档
        self.parse_pdf()
        self.authers = authers
        self.roman_num = ["I", "II", 'III', "IV", "V", "VI", "VII", "VIII", "IIX", "IX", "X"]
        self.digit_num = [str(d + 1) for d in range(10)]
        self.first_image = ''
        self.get_image_path(path[:-11])

    def parse_pdf(self):
        self.pdf = fitz.open(self.path)  # pdf文档
        self.text_list = [page.get_text() for page in self.pdf]
        self.all_text = ' '.join(self.text_list)
        self.section_page_dict = self._get_all_page_index()  # 段落与页码的对应字典
        print("section_page_dict", self.section_page_dict)
        self.section_text_dict = self._get_all_page()  # 段落与内容的对应字典
        self.section_text_dict.update({"title": self.title})
        self.section_text_dict.update({"paper_info": self.get_paper_info()})
        self.pdf.close()

    def get_paper_info(self):
        first_page_text = self.pdf[self.title_page].get_text()
        if "Abstract" in self.section_text_dict.keys():
            abstract_text = self.section_text_dict['Abstract']
        else:
            abstract_text = self.abs
        first_page_text = first_page_text.replace(abstract_text, "")
        return first_page_text

    def get_image_path(self, image_path=''):
        """
        将PDF中的第一张图保存到image.png里面，存到本地目录，返回文件名称，供gitee读取
        :param filename: 图片所在路径，"C:\\Users\\Administrator\\Desktop\\nwd.pdf"
        :param image_path: 图片提取后的保存路径
        :return:
        """
        # open file
        max_size = 0
        image_list = []
        with fitz.Document(self.path) as my_pdf_file:
            # 遍历所有页面
            for page_number in range(1, len(my_pdf_file) + 1):
                # 查看独立页面
                page = my_pdf_file[page_number - 1]
                # 查看当前页所有图片
                images = page.get_images()
                # 遍历当前页面所有图片
                for image_number, image in enumerate(page.get_images(), start=1):
                    # 访问图片xref
                    xref_value = image[0]
                    # 提取图片信息
                    base_image = my_pdf_file.extract_image(xref_value)
                    # 访问图片
                    image_bytes = base_image["image"]
                    # 获取图片扩展名
                    ext = base_image["ext"]
                    # 加载图片
                    image = Image.open(io.BytesIO(image_bytes))
                    image_size = image.size[0] * image.size[1]
                    if image_size > max_size:
                        max_size = image_size
                    image_list.append(image)
        for image in image_list:
            image_size = image.size[0] * image.size[1]
            if image_size == max_size:
                image_name = f"image.{ext}"
                im_path = os.path.join(image_path, image_name)
                print("im_path:", im_path)

                max_pix = 1960
                origin_min_pix = min(image.size[0], image.size[1])

                if image.size[0] > image.size[1]:
                    min_pix = int(image.size[1] * (max_pix / image.size[0]))
                    newsize = (max_pix, min_pix)
                else:
                    min_pix = int(image.size[0] * (max_pix / image.size[1]))
                    newsize = (min_pix, max_pix)
                image = image.resize(newsize)
                
                try:
                  image.save(open(im_path, "wb"))
                except Exception as e:
                  print('Error:',e)
                  
                return im_path, ext
        return None, None

    # 定义一个函数，根据字体的大小，识别每个章节名称，并返回一个列表
    def get_chapter_names(self, ):
        # # 打开一个pdf文件
        doc = fitz.open(self.path)  # pdf文档
        text_list = [page.get_text() for page in doc]
        all_text = ''
        for text in text_list:
            all_text += text
        # # 创建一个空列表，用于存储章节名称
        chapter_names = []
        for line in all_text.split('\n'):
            line_list = line.split(' ')
            if '.' in line:
                point_split_list = line.split('.')
                space_split_list = line.split(' ')
                if 1 < len(space_split_list) < 5:
                    if 1 < len(point_split_list) < 5 and (
                            point_split_list[0] in self.roman_num or point_split_list[0] in self.digit_num):
                        print("line:", line)
                        chapter_names.append(line)
                    # 这段代码可能会有新的bug，本意是为了消除"Introduction"的问题的！
                    elif 1 < len(point_split_list) < 5:
                        print("line:", line)
                        chapter_names.append(line)

        return chapter_names

    def get_title(self):
        doc = self.pdf  # 打开pdf文件
        max_font_size = 0  # 初始化最大字体大小为0
        max_string = ""  # 初始化最大字体大小对应的字符串为空
        max_font_sizes = [0]
        for page_index, page in enumerate(doc):  # 遍历每一页
            text = page.get_text("dict")  # 获取页面上的文本信息
            blocks = text["blocks"]  # 获取文本块列表
            for block in blocks:  # 遍历每个文本块
                if block["type"] == 0 and len(block['lines']):  # 如果是文字类型
                    if len(block["lines"][0]["spans"]):
                        font_size = block["lines"][0]["spans"][0]["size"]  # 获取第一行第一段文字的字体大小
                        max_font_sizes.append(font_size)
                        if font_size > max_font_size:  # 如果字体大小大于当前最大值
                            max_font_size = font_size  # 更新最大值
                            max_string = block["lines"][0]["spans"][0]["text"]  # 更新最大值对应的字符串
        max_font_sizes.sort()
        print("max_font_sizes", max_font_sizes[-10:])
        cur_title = ''
        for page_index, page in enumerate(doc):  # 遍历每一页
            text = page.get_text("dict")  # 获取页面上的文本信息
            blocks = text["blocks"]  # 获取文本块列表
            for block in blocks:  # 遍历每个文本块
                if block["type"] == 0 and len(block['lines']):  # 如果是文字类型
                    if len(block["lines"][0]["spans"]):
                        cur_string = block["lines"][0]["spans"][0]["text"]  # 更新最大值对应的字符串
                        font_flags = block["lines"][0]["spans"][0]["flags"]  # 获取第一行第一段文字的字体特征
                        font_size = block["lines"][0]["spans"][0]["size"]  # 获取第一行第一段文字的字体大小
                        # print(font_size)
                        if abs(font_size - max_font_sizes[-1]) < 0.3 or abs(font_size - max_font_sizes[-2]) < 0.3:
                            # print("The string is bold.", max_string, "font_size:", font_size, "font_flags:", font_flags)                            
                            if len(cur_string) > 4 and "arXiv" not in cur_string:
                                # print("The string is bold.", max_string, "font_size:", font_size, "font_flags:", font_flags) 
                                if cur_title == '':
                                    cur_title += cur_string
                                else:
                                    cur_title += ' ' + cur_string
                            self.title_page = page_index
                            # break
        title = cur_title.replace('\n', ' ')
        return title

    def _get_all_page_index(self):
        # 定义需要寻找的章节名称列表
        section_list = ["Abstract",
                        'Introduction', 'Related Work', 'Background',

                        "Introduction and Motivation", "Computation Function", " Routing Function",

                        "Preliminary", "Problem Formulation",
                        'Methods', 'Methodology', "Method", 'Approach', 'Approaches',
                        # exp
                        "Materials and Methods", "Experiment Settings",
                        'Experiment', "Experimental Results", "Evaluation", "Experiments",
                        "Results", 'Findings', 'Data Analysis',
                        "Discussion", "Results and Discussion", "Conclusion",
                        'References']
        # 初始化一个字典来存储找到的章节和它们在文档中出现的页码
        section_page_dict = {}
        # 遍历每一页文档
        for page_index, page in enumerate(self.pdf):
            # 获取当前页面的文本内容
            cur_text = page.get_text()
            # 遍历需要寻找的章节名称列表
            for section_name in section_list:
                # 将章节名称转换成大写形式
                section_name_upper = section_name.upper()
                # 如果当前页面包含"Abstract"这个关键词
                if "Abstract" == section_name and section_name in cur_text:
                    # 将"Abstract"和它所在的页码加入字典中
                    section_page_dict[section_name] = page_index
                # 如果当前页面包含章节名称，则将章节名称和它所在的页码加入字典中
                else:
                    if section_name + '\n' in cur_text:
                        section_page_dict[section_name] = page_index
                    elif section_name_upper + '\n' in cur_text:
                        section_page_dict[section_name] = page_index
        # 返回所有找到的章节名称及它们在文档中出现的页码
        return section_page_dict

    def _get_all_page(self):
        """
        获取PDF文件中每个页面的文本信息，并将文本信息按照章节组织成字典返回。

        Returns:
            section_dict (dict): 每个章节的文本信息字典，key为章节名，value为章节文本。
        """
        text = ''
        text_list = []
        section_dict = {}

        # 再处理其他章节：
        text_list = [page.get_text() for page in self.pdf]
        for sec_index, sec_name in enumerate(self.section_page_dict):
            print(sec_index, sec_name, self.section_page_dict[sec_name])
            if sec_index <= 0 and self.abs:
                continue
            else:
                # 直接考虑后面的内容：
                start_page = self.section_page_dict[sec_name]
                if sec_index < len(list(self.section_page_dict.keys())) - 1:
                    end_page = self.section_page_dict[list(self.section_page_dict.keys())[sec_index + 1]]
                else:
                    end_page = len(text_list)
                print("start_page, end_page:", start_page, end_page)
                cur_sec_text = ''
                if end_page - start_page == 0:
                    if sec_index < len(list(self.section_page_dict.keys())) - 1:
                        next_sec = list(self.section_page_dict.keys())[sec_index + 1]
                        if text_list[start_page].find(sec_name) == -1:
                            start_i = text_list[start_page].find(sec_name.upper())
                        else:
                            start_i = text_list[start_page].find(sec_name)
                        if text_list[start_page].find(next_sec) == -1:
                            end_i = text_list[start_page].find(next_sec.upper())
                        else:
                            end_i = text_list[start_page].find(next_sec)
                        cur_sec_text += text_list[start_page][start_i:end_i]
                else:
                    for page_i in range(start_page, end_page):
                        #                         print("page_i:", page_i)
                        if page_i == start_page:
                            if text_list[start_page].find(sec_name) == -1:
                                start_i = text_list[start_page].find(sec_name.upper())
                            else:
                                start_i = text_list[start_page].find(sec_name)
                            cur_sec_text += text_list[page_i][start_i:]
                        elif page_i < end_page:
                            cur_sec_text += text_list[page_i]
                        elif page_i == end_page:
                            if sec_index < len(list(self.section_page_dict.keys())) - 1:
                                next_sec = list(self.section_page_dict.keys())[sec_index + 1]
                                if text_list[start_page].find(next_sec) == -1:
                                    end_i = text_list[start_page].find(next_sec.upper())
                                else:
                                    end_i = text_list[start_page].find(next_sec)
                                cur_sec_text += text_list[page_i][:end_i]
                section_dict[sec_name] = cur_sec_text.replace('-\n', '').replace('\n', ' ')
        return section_dict


# 定义Reader类
class Reader:
    # 初始化方法，设置属性
    def __init__(self, key_word, query,
                 root_path='./',
                 gitee_key='',
                 sort=None, 
                 user_name='defualt', max_token_num = 4096, args=None):
        self.user_name = user_name  # 读者姓名
        self.key_word = key_word  # 读者感兴趣的关键词
        self.query = query  # 读者输入的搜索查询
        self.sort = sort  # 读者选择的排序方式
        self.args = args
        if args.language == 'en':
            self.language = 'English'
        elif args.language == 'zh':
            self.language = 'Chinese'
        else:
            self.language = 'Chinese'
        self.root_path = root_path
        # 创建一个ConfigParser对象
        self.config = configparser.ConfigParser()
        # 读取配置文件
        self.config.read('apikey.ini')
        #OPENAI_KEY = os.environ.get("OPENAI_KEY", "")
        # 获取某个键对应的值        
        #self.chat_api_list = self.config.get('OpenAI', 'OPENAI_API_KEYS')[1:-1].replace('\'', '').split(',')
        #self.chat_api_list.append(OPENAI_KEY)

        # prevent short strings from being incorrectly used as API keys.
        # self.chat_api_list = [api.strip() for api in self.chat_api_list if len(api) > 20]
        # self.cur_api = 0
        self.file_format = args.file_format
        if args.save_image:
            self.gitee_key = self.config.get('Gitee', 'api')
        else:
            self.gitee_key = ''
        self.max_token_num = max_token_num
        self.encoding = tiktoken.get_encoding("gpt2")

    # 定义一个函数，根据关键词和页码生成arxiv搜索链接
    def get_url(self, keyword, page):
        base_url = "https://arxiv.org/search/?"
        params = {
            "query": keyword,
            "searchtype": "all",  # 搜索所有字段
            "abstracts": "show",  # 显示摘要
            "order": "-announced_date_first",  # 按日期降序排序
            "size": 50  # 每页显示50条结果
        }
        if page > 0:
            params["start"] = page * 50  # 设置起始位置
        return base_url + requests.compat.urlencode(params)

    # 定义一个函数，根据链接获取网页内容，并解析出论文标题
    def get_titles(self, url, days=1):
        titles = []
        # 创建一个空列表来存储论文链接
        links = []
        dates = []
        #print("进入 get_titles")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("li", class_="arxiv-result")  # 找到所有包含论文信息的li标签
        #print("get_titles 获取文章成功")
        today = datetime.date.today()
        last_days = datetime.timedelta(days=days)
        for article in articles:
            try:
                title = article.find("p", class_="title").text  # 找到每篇论文的标题，并去掉多余的空格和换行符
                #print("get_titles 找到标题")
                link = article.find("span").find_all("a")[0].get('href')
                #print("get_titles 找到链接")
                date_text = article.find("p", class_="is-size-7").text
                date_text = date_text.split('\n')[0].split("Submitted ")[-1].split("; ")[0]
                date_text = datetime.datetime.strptime(date_text, "%d %B, %Y").date()
                #print("get_titles 找到时间")
                if today - date_text <= last_days:
                    titles.append(title.strip())
                    links.append(link)
                    dates.append(date_text)
            except:
                print("该文章出错：", article.find("p", class_="title").text)
            # print("links:", links)
        #print("get_titles 返回文章")
        return titles, links, dates

    # 定义一个函数，根据关键词获取所有可用的论文标题，并打印出来
    def get_all_titles_from_web(self, keyword, page_num=1, days=1):
        title_list, link_list, date_list = [], [], []
        for page in range(page_num):
            url = self.get_url(keyword, page)  # 根据关键词和页码生成链接
            print(url)
            print(days)
            titles, links, dates = self.get_titles(url, days)  # 根据链接获取论文标题
            if not titles:  # 如果没有获取到任何标题，说明已经到达最后一页，退出循环
                break
            for title_index, title in enumerate(titles):  # 遍历每个标题，并打印出来
                print(page, title_index, title, links[title_index], dates[title_index])
            title_list.extend(titles)
            link_list.extend(links)
            date_list.extend(dates)
        print("-" * 40)
        return title_list, link_list, date_list

    def get_arxiv(self, max_results=30):
        search = arxiv.Search(query=self.query,
                              max_results=max_results,
                              sort_by=self.sort,
                              sort_order=arxiv.SortOrder.Descending,
                              )
        return search

    def get_arxiv_web(self, args, page_num=1, days=2, useremail='', check='0'):
        titles, links, dates = self.get_all_titles_from_web(args.query, page_num=page_num, days=days)
        print("get_all_titles_from_web 函数运行成功")
        paper_list = []
        #print(titles)
        valid_titles = [self.validateTitle(title) for title in titles]
        print(valid_titles)
        #print(valid_titles)
        #print(list_articles()['gcarticles'])
        #print([row[0] for row in list_articles()['gcarticles']])
        exist_articles = [row[0] for row in list_articles('','')['gcarticles']]
        print(exist_articles)

        user_exist_articles = [row[0] for row in list_articles(useremail,'')['gcarticles']]

        user_result_index = [i for i, x in enumerate(valid_titles) if not any(substring in x for substring in user_exist_articles)]

        result_index = [i for i, x in enumerate(valid_titles) if not any(substring in x for substring in exist_articles)]

        set1 = set(user_result_index)
        set2 = set(result_index)

        user_db_add_index = list(set1 - set2)
        user_titles = [titles[i] for i in user_db_add_index]

        if check == '1':
            db = Database(**config)
            export_path = os.path.join(self.root_path, 'export')
            for i in range(len(user_titles)):
                db.insert("gcarticles",f"('{self.validateTitle(user_titles[i])[:80]}','{os.path.join(export_path,self.validateTitle(user_titles[i])[:80])}',0,'{args.query}','{args.key_word}', 0, '{useremail}')")
        # print(result_index)
        # print('------------------------')
        # print(titles)
        # print('------------------------')
        # print([titles[i] for i in result_index])
        # print('------------------------')
        # print([links[i] for i in result_index])
        # print([dates[i] for i in result_index])

        titles = [titles[i] for i in result_index]
        links = [links[i] for i in result_index]
        dates = [dates[i] for i in result_index]

        print('------------------------')
        print(titles)
        print('本次可增文章数量为：', len(titles))
        print('------------------------')

        if check == '0':
            return paper_list, user_titles + titles


        for title_index, title in enumerate(titles):
            if title_index + 1 > args.max_results:
                break
            print(title_index, title, links[title_index], dates[title_index])
            url = links[title_index] + ".pdf"  # the link of the pdf document
            filename = self.try_download_pdf(url, title)
            paper = Paper(path=filename,
                          date=dates[title_index],
                          url=links[title_index],
                          title=title,
                          )
            paper_list.append(paper)
        print('------------------------')
        print('本次新增文章数量为：', len(paper_list))
        print('------------------------')
        return paper_list, user_titles

    def validateTitle(self, title):
        # 将论文的乱七八糟的路径格式修正
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        return new_title

    def download_pdf(self, url, title):
        response = requests.get(url)  # send a GET request to the url
        date_str = str(datetime.datetime.now())[:13].replace(' ', '-')
        path = self.root_path + 'export/' + self.validateTitle(title)[:80]  # 原先用了 [:80] 的限制把文章标题截断了
        try:
            os.makedirs(path)
        except:
            pass
        filename = os.path.join(path, 'article.pdf')
        with open(filename, "wb") as f:  # open a file with write and binary mode
            f.write(response.content)  # write the content of the response to the file
        return filename

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    def try_download_pdf(self, url, title):
        return self.download_pdf(url, title)

    def summary_with_chat(self, paper_list, model, useremail, query, keyword):
        htmls = []

        db = Database(**config)
        summary_num = 0
        for paper_index, paper in enumerate(paper_list):
            # 第一步先用title，abs，和introduction进行总结。
            # htmls.append('## Paper:' + str(paper_index + 1))
            text = ''
            text += 'Title:' + paper.title
            htmls.append('##' + paper.title) 
            text += 'Url:' + paper.url
            htmls.append(paper.url) 
            htmls.append(paper.date.strftime("%Y-%m-%d")) 
            text += 'Abstract:' + paper.abs
            text += 'Paper_info:' + paper.section_text_dict['paper_info']
            # intro
            text += list(paper.section_text_dict.values())[0]
            chat_summary_text = ""
            try:
                chat_summary_text = self.chat_summary(text=text, model=model)
            except Exception as e:
                print("summary_error:", e)
                if "maximum context" in str(e):
                    current_tokens_index = str(e).find("your messages resulted in") + len(
                        "your messages resulted in") + 1
                    offset = int(str(e)[current_tokens_index:current_tokens_index + 4])
                    #summary_prompt_token = offset + 1000 + 150
                    summary_prompt_token = offset + 800 + 150
                    print("summary_prompt_token",summary_prompt_token)
                    chat_summary_text = self.chat_summary(text=text, summary_prompt_token=summary_prompt_token, model=model)

            
            htmls.append('\n\n\n')            
            if "chat_summary_text" in locals():
                htmls.append(chat_summary_text)

            # 第二步总结方法：
            # TODO，由于有些文章的方法章节名是算法名，所以简单的通过关键词来筛选，很难获取，后面需要用其他的方案去优化。
            method_key = ''
            for parse_key in paper.section_text_dict.keys():
                if 'method' in parse_key.lower() or 'approach' in parse_key.lower():
                    method_key = parse_key
                    break
            
            chat_method_text = ""
            if method_key != '':
                text = ''
                method_text = ''
                summary_text = ''
                summary_text += "<summary>" + chat_summary_text
                # methods                
                method_text += paper.section_text_dict[method_key]
                text = summary_text + "\n\n<Methods>:\n\n" + method_text
                # chat_method_text = self.chat_method(text=text)
                try:
                    chat_method_text = self.chat_method(text=text, model=model)
                except Exception as e:
                    print("method_error:", e)
                    if "maximum context" in str(e):
                        current_tokens_index = str(e).find("your messages resulted in") + len(
                            "your messages resulted in") + 1
                        offset = int(str(e)[current_tokens_index:current_tokens_index + 4])
                        method_prompt_token = offset + 800 + 150
                        chat_method_text = self.chat_method(text=text, model=model, method_prompt_token=method_prompt_token)
                
                if "chat_method_text" in locals():
                    htmls.append(chat_method_text)
                # htmls.append(chat_method_text)
            else:
                chat_method_text = ''
            htmls.append("\n" * 4)

            # 第三步总结全文，并打分：
            conclusion_key = ''
            for parse_key in paper.section_text_dict.keys():
                if 'conclu' in parse_key.lower():
                    conclusion_key = parse_key
                    break

            text = ''
            conclusion_text = ''
            summary_text = ''
            summary_text += "<summary>" + chat_summary_text + "\n <Method summary>:\n" + chat_method_text
            chat_conclusion_text = ""
            if conclusion_key != '':
                # conclusion                
                conclusion_text += paper.section_text_dict[conclusion_key]
                text = summary_text + "\n\n<Conclusion>:\n\n" + conclusion_text
            else:
                text = summary_text
            # chat_conclusion_text = self.chat_conclusion(text=text)
            try:
                chat_conclusion_text = self.chat_conclusion(text=text, model=model)
            except Exception as e:
                print("conclusion_error:", e)
                if "maximum context" in str(e):
                    current_tokens_index = str(e).find("your messages resulted in") + len(
                        "your messages resulted in") + 1
                    offset = int(str(e)[current_tokens_index:current_tokens_index + 4])
                    conclusion_prompt_token = offset + 800 + 150
                    chat_conclusion_text = self.chat_conclusion(text=text,
                                                                model=model,
                                                                conclusion_prompt_token=conclusion_prompt_token)            
            if "chat_conclusion_text" in locals():
                htmls.append(chat_conclusion_text)
            htmls.append("\n" * 4)

            # # 整合成一个文件，打包保存下来。
            date_str = str(datetime.datetime.now())[:13].replace(' ', '-')
            export_path = os.path.join(self.root_path, 'export')
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            mode = 'w' # if paper_index == 0 else 'a'
            file_name = os.path.join(export_path,
                                     self.validateTitle(paper.title)[:80],"md." + self.file_format)
            self.export_to_markdown("\n".join(htmls), file_name=file_name, mode=mode)
            htmls = []

            db.insert("gcarticles",f"('{self.validateTitle(paper.title)[:80]}','{os.path.join(export_path,self.validateTitle(paper.title)[:80])}',0,'{query}','{keyword}', 0, '{useremail}')")
            summary_num = summary_num + 1
        
        return summary_num



    def modelChat(self, messages, model):
        if model == "星火":
            pass
            #result = SparkCreate(messages)
        else:
            if openai.api_key == "none":
                response = openai.ChatCompletion.create(
                    model="chatglm2-6b",
                    messages=messages,
                )
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                )
            result = ''
            for choice in response.choices:
                result += choice.message.content
        
        return result

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    def chat_conclusion(self, text, model, conclusion_prompt_token=1200):
        #openai.api_key = self.chat_api_list[self.cur_api]
        # openai.api_key = "none"
        # self.cur_api += 1
        # self.cur_api = 0 if self.cur_api >= len(self.chat_api_list) - 1 else self.cur_api
        text_token = len(self.encoding.encode(text))
        clip_text_index = int(len(text) * (self.max_token_num - conclusion_prompt_token) / text_token)
        clip_text = text[:clip_text_index]

        messages = [
            {"role": "system",
            # "content": "You are a reviewer in the field of [" + self.key_word + "] and you need to critically review this article"},
             "content": "你是一个 [" + self.key_word + "] 领域的审查员，你需要批判性地审查这篇文章"},
            # chatgpt 角色
            {"role": "assistant",
            # "content": "This is the <summary> and <conclusion> part of an English literature, where <summary> you have already summarized, but <conclusion> part, I need your help to summarize the following questions:" + clip_text},
            "content": "这是一篇英文文献的<总结>和<结论>部分，其中<summary>你已经总结过了，但是<conclusion>部分，我需要你帮助总结以下问题：" + clip_text},
            # 背景知识，可以参考OpenReview的审稿流程
            # {"role": "user", "content": """                 
            #      8. Make the following summary.Be sure to use {} answers (proper nouns need to be marked in English).
            #         - (1):What is the significance of this piece of work?
            #         - (2):Summarize the strengths and weaknesses of this article in three dimensions: innovation point, performance, and workload.                   
            #         .......
            #      Follow the format of the output later: 
            #      8. Conclusion: \n\n
            #         - (1):xxx;\n                     
            #         - (2):Innovation point: xxx; Performance: xxx; Workload: xxx;\n                      
                 
            #      Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not repeat the content of the previous <summary>, the value of the use of the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed, ....... means fill in according to the actual requirements, if not, you can not write.                 
            #      """.format(self.language, self.language)},
            # 一定要使用{}答案（专有名词需要用英文标注），陈述尽可能简洁、学术，不要重复前面<summary>的内容，使用原数字的值，一定要 要严格按照格式，将相应内容输出到xxx，按照\n换行，.......表示按照实际要求填写，如果没有，可以不写。
            {"role": "user", "content": """ 
                  8. 做如下总结。一定要用{}答案（专有名词需用英文标注）。
                     - (1):这部作品的意义是什么？
                     - (2):从创新点、性能、工作量三个维度总结本文的优缺点。
                     .......
                  按照后面输出的格式：
                  8.结论：\n\n
                     - (1):xxx;\n
                     - (2):创新点：xxx； 性能表现：xxx； 工作量：xxx；\n
                 
                  Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not repeat the content of the previous <summary>, the value of the use of the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed, ....... means fill in according to the actual requirements, if not, you can not write.
                  """.format(self.language, self.language)},
        ]

        result = self.modelChat(messages, model)
        print("conclusion_result:\n", result)
        # print("prompt_token_used:", response.usage.prompt_tokens,
        #       "completion_token_used:", response.usage.completion_tokens,
        #       "total_token_used:", response.usage.total_tokens)
        # print("response_time:", response.response_ms / 1000.0, 's')
        return result

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    def chat_method(self, text, model, method_prompt_token=1200):
        ## openai.api_key = self.chat_api_list[self.cur_api]
        # openai.api_key = "none"
        # self.cur_api += 1
        # self.cur_api = 0 if self.cur_api >= len(self.chat_api_list) - 1 else self.cur_api
        text_token = len(self.encoding.encode(text))
        clip_text_index = int(len(text) * (self.max_token_num - method_prompt_token) / text_token)
        clip_text = text[:clip_text_index]
        messages = [
            {"role": "system",
            # "content": "You are a researcher in the field of [" + self.key_word + "] who is good at summarizing papers using concise statements"},
             "content": "你是一个 [" + self.key_word + "] 领域的审查员，你需要批判性地审查这篇文章"},
            # chatgpt 角色
            {"role": "assistant",
            # "content": "This is the <summary> and <Method> part of an English document, where <summary> you have summarized, but the <Methods> part, I need your help to read and summarize the following questions." + clip_text},
            "content": "这是一篇英文文献的<summary>和<Method>部分，其中<summary>你已经总结过了，但是<Method>部分，我需要你帮助总结以下问题：" + clip_text},
            # 背景知识
            # {"role": "user", "content": """                 
            #      7. Describe in detail the methodological idea of this article. Be sure to use {} answers (proper nouns need to be marked in English). For example, its steps are.
            #         - (1):...
            #         - (2):...
            #         - (3):...
            #         - .......
            #      Follow the format of the output that follows: 
            #      7. Methods: \n\n
            #         - (1):xxx;\n 
            #         - (2):xxx;\n 
            #         - (3):xxx;\n  
            #         ....... \n\n     
                 
            #      Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not repeat the content of the previous <summary>, the value of the use of the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed, ....... means fill in according to the actual requirements, if not, you can not write.                 
            #      """.format(self.language, self.language)},
            # 一定要使用{}答案（专有名词需要用英文标注），陈述尽可能简洁、学术，不要重复前面<summary>的内容，使用原数字的值，一定要 要严格按照格式，将相应内容输出到xxx，按照\n换行，.......表示按照实际要求填写，如果没有，可以不写。
            {"role": "user", "content": """                 
                7. 详细描述本文的方法论思想。 请务必使用 {} 答案（专有名词需要用英文标记）。 例如，其步骤是。
                     - (1):...
                     - (2):...
                     - (3):...
                     - .......
                  请遵循以下输出格式：
                 7. 方法：\n\n
                     - (1):xxx;\n
                     - (2):xxx;\n
                     - (3):xxx;\n
                     ......\n\n
                 
                  Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not repeat the content of the previous <summary>, the value of the use of the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed, ....... means fill in according to the actual requirements, if not, you can not write.
                """.format(self.language, self.language)},
        ]

        result = self.modelChat(messages, model)
        print("method_result:\n", result)
        # print("prompt_token_used:", response.usage.prompt_tokens,
        #       "completion_token_used:", response.usage.completion_tokens,
        #       "total_token_used:", response.usage.total_tokens)
        # print("response_time:", response.response_ms / 1000.0, 's')
        return result

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
                    stop=tenacity.stop_after_attempt(5),
                    reraise=True)
    def chat_summary(self, text, model, summary_prompt_token=1100):
        # openai.api_key = self.chat_api_list[self.cur_api]
        # openai.api_key = "none"
        # self.cur_api += 1
        # self.cur_api = 0 if self.cur_api >= len(self.chat_api_list) - 1 else self.cur_api
        text_token = len(self.encoding.encode(text))
        print('text_token',text_token)
        clip_text_index = int(len(text) * (self.max_token_num - summary_prompt_token) / text_token)
        print('clip_text_index',clip_text_index)
        clip_text = text[:clip_text_index]
        print('clip_text',len(clip_text))
        messages = [
            {"role": "system",
            # "content": "You are a researcher in the field of [" + self.key_word + "] who is good at summarizing papers using concise statements"},
             "content": "你是一个 [" + self.key_word + "] 领域的审查员，你需要批判性地审查这篇文章"},
            {"role": "assistant",
            # "content": "This is the title, author, link, abstract and introduction of an English document. I need your help to read and summarize the following questions: " + clip_text},
            "content": "这是一篇英文文献的标题，作者，链接，摘要和介绍，我需要你的帮助来阅读并总结以下问题：" + clip_text},
            # {"role": "user", "content": """                 
            #      1. Mark the title of the paper (with Chinese translation)
            #      2. list all the authors' names (use English)
            #      3. mark the first author's affiliation (output {} translation only)                 
            #      4. mark the keywords of this article (use English)
            #      5. link to the paper, Github code link (if available, fill in Github:None if not)
            #      6. summarize according to the following four points.Be sure to use {} answers (proper nouns need to be marked in English)
            #         - (1):What is the research background of this article?
            #         - (2):What are the past methods? What are the problems with them? Is the approach well motivated?
            #         - (3):What is the research methodology proposed in this paper?
            #         - (4):On what task and what performance is achieved by the methods in this paper? Can the performance support their goals?
            #      Follow the format of the output that follows:                  
            #      1. Title: xxx\n\n
            #      2. Authors: xxx\n\n
            #      3. Affiliation: xxx\n\n                 
            #      4. Keywords: xxx\n\n   
            #      5. Urls: xxx or xxx , xxx \n\n      
            #      6. Summary: \n\n
            #         - (1):xxx;\n 
            #         - (2):xxx;\n 
            #         - (3):xxx;\n  
            #         - (4):xxx.\n\n     
                 
            #      Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not have too much repetitive information, numerical values using the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed.                 
            #      """.format(self.language, self.language, self.language)},
            # 务必使用{}答案（专有名词需用英文标注），陈述尽量简洁、学术，不要有太多重复信息，数值使用原数，一定要严格遵循格式， 相应内容输出到xxx，按照\n换行。
            {"role": "user", "content": """                 
                 1.标注论文标题（附中文翻译）
                  2.列出所有作者姓名（使用英文）
                  3.标记第一作者单位（仅输出{}译文）
                  4.标记本文的关键词（使用英文）
                  5.论文链接、Github代码链接（如果有则填写Github:None，如果没有）
                  6.根据以下四点进行内容概括。一定要用{}答案（专有名词需用英文标注）
                     - (1):本文的研究背景是什么？
                     - (2):过去的方法是什么？ 他们有什么问题？ 该方法的动机是否良好？
                     - (3):本文提出的研究方法是什么？
                     - (4)：本文的方法实现了哪些任务和哪些性能？ 绩效能否支持他们的目标？
                  请遵循以下输出格式：
                  1. 标题：xxx\n\n
                  2. 作者：xxx\n\n
                  3. 所属单位：xxx\n\n
                  4. 关键字：xxx\n\n
                  5. 网址： xxx 或 xxx , xxx \n\n
                  6. 内容概括：\n\n
                     - (1):xxx;\n
                     - (2):xxx;\n
                     - (3):xxx;\n
                     - (4):xxx。\n\n
                 
                 Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not have too much repetitive information, numerical values using the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed.                 
                 """.format(self.language, self.language, self.language)},
        ]
        
        result = self.modelChat(messages, model)
        print("summary_result:\n", result)
        # print("prompt_token_used:", response.usage.prompt_tokens,
        #       "completion_token_used:", response.usage.completion_tokens,
        #       "total_token_used:", response.usage.total_tokens)
        # print("response_time:", response.response_ms / 1000.0, 's')
        return result

    def export_to_markdown(self, text, file_name, mode='w'):
        # 打开一个文件，以写入模式
        with open(file_name, mode, encoding="utf-8") as f:
            # 将html格式的内容写入文件
            f.write(text)

    # 定义一个方法，打印出读者信息
    def show_info(self):
        print(f"Key word: {self.key_word}")
        print(f"Query: {self.query}")
        print(f"Sort: {self.sort}")

import pymysql


class Database():
    # **config是指连接数据库时需要的参数,这样只要参数传入正确，连哪个数据库都可以
    # 初始化时就连接数据库
    def __init__(self, **config):
        try:
            # 连接数据库的参数我不希望别人可以动，所以设置私有
            self.__conn = pymysql.connect(**config)
            self.__cursor = self.__conn.cursor()
        except Exception as e:
            print

    # 查询一条数据
    # 参数：表名table_name,条件factor_str,要查询的字段field 默认是查询所有字段*
    def select_one(self, table_name, factor_str='', field="*"):
        if factor_str == '':
            sql = f"select {field} from {table_name}"
        else:
            sql = f"select {field} from {table_name} where {factor_str}"
        self.__cursor.execute(sql)
        return self.__cursor.fetchone()

    # 查询多条数据
    # 参数：要查询数据的条数num,表名table_name,条件factor_str,要查询的字段field 默认是查询所有字段*
    def select_many(self, num, table_name, factor_str='', field="*"):
        if factor_str == '':
            sql = f"select {field} from {table_name}"
        else:
            sql = f"select {field} from {table_name} where {factor_str}"
        self.__cursor.execute(sql)
        return self.__cursor.fetchmany(num)

    # 查询全部数据
    # 参数：表名table_name,条件factor_str,要查询的字段field 默认是查询所有字段*
    def select_all(self, table_name, factor_str='', field="*"):
        if factor_str == '':
            sql = f"select {field} from {table_name}"
        else:
            sql = f"select {field} from {table_name} where {factor_str}"
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    # 新增数据
    def insert(self,table_name, value):
        sql = f"insert into {table_name} values {value}"
        try:
            self.__cursor.execute(sql)
            self.__conn.commit()
            print("插入成功")
        except Exception as e:
            print("插入失败\n", e)
            self.__conn.rollback()

    # 修改数据
    # 参数：表名，set值(可能是一个，也可能是多个，所以用字典)，条件
    def update(self, table_name, val_obl,change_str):
        sql = f"update {table_name} set"
        # set后面应该是要修改的字段，但是可能会修改多个字段的值，所以遍历一下
        # key对应字段的名，val对应字段的值
        for key, val in val_obl.items():
            if isinstance(val, str):
                sql += f" {key} = '{val}',"
            else:
                sql += f" {key} = {val},"
        # 遍历完的最后面会有一个逗号，所以给它切掉，然后再拼接条件
        # !!!空格很重要
        sql = sql[:-1]+" where "+change_str
        #print(sql)
        try:
            self.__cursor.execute(sql)
            self.__conn.commit()
            print("修改成功")
        except Exception as e:
            print("修改失败\n", e)
            self.__conn.rollback()

    # 删除数据
    def delete(self,table_name, item):
        sql = f"delete from {table_name} where {item}"
        try:
            self.__cursor.execute(sql)
            self.__conn.commit()
            print("删除成功")
        except Exception as e:
            print("删除失败\n", e)
            self.__conn.rollback()

    # 查询数量
    def count(self, table_name, change_str):
        if change_str == '':
            sql = f"SELECT COUNT(*) as count FROM gcarticles"
        else:
            sql = f"SELECT COUNT(*) as count FROM gcarticles where {change_str}"
        self.__cursor.execute(sql)
        result = self.__cursor.fetchone()
        count = result
        return count



def read_md(
    filename: str = Body(..., description="path", example="/home/huawei/nxy/bbft/ChatPaper/export/In-context Autoencoder for Context Compression in a Large Language Model/md.md"),
    x: str = Body(..., description="", example="")
):
    import markdown
    print(filename)
    try:
        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()
            html = markdown.markdown(text)
            print(text)
            return {"content": html}
    except FileNotFoundError:
        try:
            dir_name = filename.split('/')[-2][:80]
            filename = filename.replace(filename.split('/')[-2], dir_name)
            with open(filename[:80], "r", encoding="utf-8") as file:
                text = file.read()
                html = markdown.markdown(text)
                print(text)
                return {"content": html}
        except FileNotFoundError:
            return {"error": "File not found."}
            
        return {"error": "File not found."}
  
def spark_translate(
    filename: str = Body(..., description="path", example="/home/huawei/nxy/bbft/ChatPaper/export/In-context Autoencoder for Context Compression in a Large Language Model/md.md"),
    x: str = Body(..., description="", example="")
):
    from spark.Spark_trans import 解析PDF
    print(filename)
    save_path = filename[:-12]
    print(save_path)
    title = save_path.split('/')[-1]
    print(title)
    
    try:
        解析PDF(filename, save_path)
        
        db = Database(**config)
        db.update("gcarticles", {"translated": 1}, "name='"+title+"'")
        return {"success": 1}
    except FileNotFoundError:
        return {"error": "File not found."}     
        
def search_spark_translate(
    filename: str = Body(..., description="path", example="/home/huawei/nxy/bbft/ChatPaper/export/In-context Autoencoder for Context Compression in a Large Language Model/md.md"),
    x: str = Body(..., description="", example="")
):
    from spark.Spark_trans import 解析PDF
    print(filename)
    save_path = filename[:-12]
    print(save_path)
    title = save_path.split('/')[-1]
    print(title)
    
    try:
        db = Database(**config)
        select_all = db.select_all("gcarticles", "name='"+title+"'")
        return {"result": select_all}
    except FileNotFoundError:
        return {"error": "File not found."}
    
def list_articles( 
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    query: str = Body(..., description="query", example="Brain computer interface")
    ):
    try:
        db = Database(**config)
        if useremail != '':
            if query != '':
                select_all = db.select_all("gcarticles", "useremail='"+useremail+"' AND query='"+query+"'")
            else:
                select_all = db.select_all("gcarticles", "useremail='"+useremail+"'")
        else:
            select_all = db.select_all("gcarticles")
        
        return {"gcarticles": select_all}
    except FileNotFoundError:
        return {"error": "List articles error."}
    
def count_articles(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    x: str = Body(..., description="", example="")
):
    try:
        db = Database(**config)
        count = db.count("gcarticles", "useremail='"+useremail+"'")
        
        return {"num": count}
    except FileNotFoundError:
        return {"error": "Count articles error."}
        
def update_articles(
    value: str = Body(..., description="state", example="0"),
    title: str = Body(..., description="", example="")
    ):
    try:
        if value == "0":
            submitted = 1
        else:
            submitted = 0
        
        db = Database(**config)
        print("gcarticles", {"submitted": submitted}, "name='"+title+"'")
        db.update("gcarticles", {"submitted": submitted}, "name='"+title+"'")
        
        return {"state": "success"}
    except FileNotFoundError:
        return {"error": "List articles error."}

def list_query_category(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    x: str = Body(..., description="", example="")
):
    db = Database(**config)
    select_all = db.select_all(field = "query, COUNT(*) as count", table_name = "gcarticles WHERE useremail='"+useremail+"' GROUP BY query")

    return {"res": select_all}
    
def delete_redundance():
    db = Database(**config)
    table_name = "gcarticles"

    folder_path = "/home/huawei/nxy/bbft/ChatPaper/export/"  # 替换为你实际的文件夹路径
    folders = [f.name for f in os.scandir(folder_path) if f.is_dir()]

    # 删除数据库中没有文件的条目
    exist_articles = [row[0] for row in list_articles()['gcarticles']]
    delete_database_num = 0
    for exist in exist_articles:
        item = "name='" + exist + "'"
        if exist not in folders:
            db.delete(table_name, item)
            delete_database_num = delete_database_num + 1
        
    # 删除没有翻译的文件夹
    delete_num = 0
    for folder in folders:
        folder_path = "/home/huawei/nxy/bbft/ChatPaper/export/" + folder
        item = "name='" + folder + "'"
        if os.path.exists(folder_path):
            # 使用glob获取指定文件夹下所有.md文件
            md_files = glob.glob(os.path.join(folder_path, '*.md'))
            # 检查是否存在.md文件
            if not md_files:
                # 删除空文件夹
                file_list = os.listdir(folder_path)
                # 删除文件夹中的所有文件
                for filename in file_list:
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(folder_path)
                print(f"Folder '{folder_path}' does not contain any .md file and has been deleted.")
                db.delete(table_name, item)
                delete_num = delete_num + 1
            else:
                with open(os.path.join(folder_path, 'md.md'), 'r') as file:
                    lines = file.readlines()
                    line_count = len(lines)
                if line_count < 20:
                    # 删除空文件夹
                    file_list = os.listdir(folder_path)
                    # 删除文件夹中的所有文件
                    for filename in file_list:
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(folder_path)
                    print(f"Folder '{folder_path}' does not contain any .md file and has been deleted.")
                    db.delete(table_name, item)
                    delete_num = delete_num + 1

                print(f"Folder '{folder_path}' contains .md files.")

    return {"folder_num": delete_num, "database_num": delete_database_num}
                


def download_file(
    filename: str = Body(..., description="path", example="/home/huawei/nxy/bbft/ChatPaper/export/In-context Autoencoder for Context Compression in a Large Language Model/md.md"),
    x: str = Body(..., description="", example="")
    ):
    from fastapi.responses import FileResponse
    
    try:
        file_path = filename  # 替换为你实际的文件路径
        print(file_path)
        
        return FileResponse(file_path, filename=filename.split('//')[-1])
    except FileNotFoundError:
        return {"error": "File not found."}
        
def get_image(
    filename: str = Body(..., description="path", example="/home/huawei/nxy/bbft/ChatPaper/export/In-context Autoencoder for Context Compression in a Large Language Model/"),
    x: str = Body(..., description="", example="")
    ):
    # 假设你有一个名为 "image.jpg" 的图片文件
    from fastapi.responses import StreamingResponse
    directory = filename  # 替换为你实际的图片路径
    image_extensions = [".jpg", ".jpeg", ".png", ".gif"]  # 支持的图片文件扩展名列表
    
    image_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in image_extensions:
                image_files.append(os.path.join(root, file))
                
    if len(image_files)>0:
        image_path = image_files[0]
        def stream_image():
            with open(image_path, "rb") as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    yield chunk
  
        return StreamingResponse(stream_image(), media_type="image/jpeg")
    else:
        directory = filename[:80]  # 替换为你实际的图片路径
        dir_name = filename.split('/')[-2][:80]
        directory = filename.replace(filename.split('/')[-2], dir_name)
        image_extensions = [".jpg", ".jpeg", ".png", ".gif"]  # 支持的图片文件扩展名列表
        
        image_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in image_extensions:
                    image_files.append(os.path.join(root, file))

        if len(image_files)>0:
            image_path = image_files[0]
            def stream_image():
                with open(image_path, "rb") as file:
                    while True:
                        chunk = file.read(1024)
                        if not chunk:
                            break
                        yield chunk
    
            return StreamingResponse(stream_image(), media_type="image/jpeg")
        else:
            return {"error": "File not found."}

    
def update_database():
    # 保存结果到数据库
    folder_path = "/home/huawei/nxy/bbft/ChatPaper/export/"  # 替换为你实际的文件夹路径
    folders = [f.name for f in os.scandir(folder_path) if f.is_dir()]
    
    db = Database(**config)
    insert_num = 0
    for folder in folders:
        folder_path = "/home/huawei/nxy/bbft/ChatPaper/export/" + folder
        if os.path.exists(folder_path):
            # 使用glob获取指定文件夹下所有.md文件
            md_files = glob.glob(os.path.join(folder_path, '*.md'))
            # 检查是否存在.md文件
            if not md_files:
                # 删除空文件夹
                file_list = os.listdir(folder_path)
                # 删除文件夹中的所有文件
                for filename in file_list:
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(folder_path)
                print(f"Folder '{folder_path}' does not contain any .md file and has been deleted.")
            else:
                print(f"Folder '{folder_path}' contains .md files.")
                db.insert("gcarticles",f"('{folder}','{folder_path}',0,'Brain computer interface','', 0)")
                insert_num = insert_num + 1

    return {"num": len(folders), "insert_num": insert_num}

def update_database_path(
    path: str = Body(..., description="path", example="D:/AI/bbft/ChatPaper/export/"),
    x: str = Body(..., description="", example="")
    ):
    db = Database(**config)
    select_all = db.select_all("gcarticles")
    for item in select_all:
        # print(item)
        # 新路径地址
        new_path = path + item[0]
        #print(new_path)
        #print({"path": f'{new_path}'})
        db.update("gcarticles", {"path": f'{new_path}'}, "name='"+item[0]+"'")


def chat_arxiv_main(
    query: str = Body(..., description="query", example="GPT-4"),
    keyword: str = Body(..., description="keyword", example="GPT robot"),
    pagenum: str = Body(..., description="page_num", example="1"),
    maxresults: str = Body(..., description="max_results", example="the maximum number of results"),
    days: str = Body(..., description="days", example="3"),
    model: str = Body(..., description="model", example="chatglm2"),
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    check: str = Body(..., description="check", example="0 or 1"),
):
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default=query, help="the query string, ti: xx, au: xx, all: xx,")
    parser.add_argument("--key_word", type=str, default=keyword, help="the key word of user research fields")
    parser.add_argument("--page_num", type=int, default=int(pagenum), help="the maximum number of page")
    parser.add_argument("--max_results", type=int, default=int(maxresults), help="the maximum number of results")
    parser.add_argument("--days", type=int, default=int(days), help="the last days of arxiv papers of this query")
    parser.add_argument("--sort", type=str, default="web", help="another is LastUpdatedDate")
    parser.add_argument("--save_image", default=False,
                        help="save image? It takes a minute or two to save a picture! But pretty")
    parser.add_argument("--file_format", type=str, default='md', help="导出的文件格式，如果存图片的话，最好是md，如果不是的话，txt的不会乱")
    parser.add_argument("--language", type=str, default='zh', help="The other output lauguage is English, is en")

    args = ArxivParams(**vars(parser.parse_args()))
    
    if model == "ChatGLM2":
      openai.api_base = "http://localhost:8003/v1"
      openai.api_key = "none"
      max_token_num = 32000
    else:
      openai.api_base = "https://api.openai.com/v1"
      openai.proxy = "http://127.0.0.1:7890"
      #openai.api_key = "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"
      #openai.api_key = "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"
      openai.api_key = "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"
      max_token_num = 4096
    
    root_path = os.getcwd() + '/'
    reader1 = Reader(key_word=args.key_word,
                     query=args.query,
                     max_token_num = max_token_num,
                     args=args,
                     root_path=root_path
                     )
    reader1.show_info()
    
    # 保存结果到数据库
    # try:
    paper_list, user_titles = reader1.get_arxiv_web(args=args, page_num=args.page_num, days=args.days, useremail=useremail, check=check)
    print('获取文章列表成功！')

    if check == '0':
        return {"num": len(user_titles) + len(paper_list)}

    summary_num = 0
    summary_num = reader1.summary_with_chat(paper_list=paper_list, model=model, useremail=useremail, query=query, keyword=keyword)
    print('文章总结成功！')

    # 保存结果到数据库
    folder_path = "/root/bbft/ChatPaper/export/"  # 替换为你实际的文件夹路径
    folders = [f.name for f in os.scandir(folder_path) if f.is_dir()]
    
    # db = Database(**config)
    for folder in folders:
        folder_path = "/root/bbft/ChatPaper/export/" + folder
        if os.path.exists(folder_path):
            # 使用glob获取指定文件夹下所有.md文件
            md_files = glob.glob(os.path.join(folder_path, '*.md'))
            # 检查是否存在.md文件
            if not md_files:
                # 删除空文件夹
                file_list = os.listdir(folder_path)
                # 删除文件夹中的所有文件
                for filename in file_list:
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(folder_path)
                print(f"Folder '{folder_path}' does not contain any .md file and has been deleted.")
            else:
                print(f"Folder '{folder_path}' contains .md files.")
                # db.insert("gcarticles",f"('{folder}','{folder_path}',0,'{query}','{keyword}', 0, '{useremail})")

    return {"num": len(user_titles) + summary_num}
        
        # return {"folders": folders}
    # except Exception as e:
    #     print("error")
    #     return {"num": "Error."}


# 文献综述相关函数
from LiteratureReview import * 

def show_wordcloud(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    query: str = Body(..., description="", example="")
    ):
    directory_path = '/root/bbft/ChatPaper/export/'

    user_exist_articles = [row[0] for row in list_articles(useremail, query)['gcarticles']]

    #print(user_exist_articles)
    subdirectories = []
    for item in user_exist_articles:
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
        else:
            subdirectories.append(item_path[:-1])
            
    #print(subdirectories)
    success_zh, success_en, res_zh, res_en  = get_all_keyword_list_and_generate_wordclouds(subdirectories, useremail)

    save_folder = os.getcwd() + '/literatureReview/' + useremail + '/'

    path_zh = ""
    path_en = ""
    res = ""

    if success_zh == 1:
        path_zh = save_folder + 'wordcloud_zh.png'
        res += "该领域下出现频率最多的20个关键词以及频率为： \n"
        for i in range(20):
            res += str(res_zh[i][0]) + ':' + str(res_zh[i][1]) + '\n'

    if success_en == 1:
        path_en = save_folder + 'wordcloud_en.png'
        res += "The 20 most frequently occurring keywords in this field and their frequency are: \n"
        for i in range(20):
            res += str(res_en[i][0]) + ':' + str(res_en[i][1]) + '\n'

    return {"path_zh": path_zh, "path_en": path_en, "res": res}

def show_num_of_publication_per_year(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    query: str = Body(..., description="", example="")
    ):
    directory_path = '/root/bbft/ChatPaper/export/'

    user_exist_articles = [row[0] for row in list_articles(useremail, query)['gcarticles']]

    #print(user_exist_articles)
    subdirectories = []
    for item in user_exist_articles:
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
        else:
            subdirectories.append(item_path[:-1])

    md_files_info = []
    
    for file_name in subdirectories:
        file_path = file_name + '/md.md'
        with open(file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
            time, keywords = extract_info_from_md(md_content)
            md_files_info.append((time, keywords))

    pubulication_num_per_year = cul_paper_num_per_month(md_files_info)
    save_path = draw_pub_num_per_year_bar(pubulication_num_per_year, query, useremail)
    res = "领域文章数量与年份的对应关系为： \n"
    for i in pubulication_num_per_year:
        res += str(i) + ":" + str(pubulication_num_per_year[i]) + "\n"
    res += "注：该图表仅统计了文章总结包含了年份的情况"

    return {"path": save_path, "res": res}

def show_keywords_frequency_bar(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    query: str = Body(..., description="", example="")
    ):
    directory_path = '/root/bbft/ChatPaper/export/'

    user_exist_articles = [row[0] for row in list_articles(useremail, query)['gcarticles']]

    #print(user_exist_articles)
    subdirectories = []
    for item in user_exist_articles:
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
        else:
            subdirectories.append(item_path[:-1])

    _, _, res_zh, res_en = get_all_keyword_list_and_generate_wordclouds(subdirectories, useremail)

    current_path = os.getcwd()
    font_path = current_path + '/SimHei.ttf'

    path_zh = ""
    path_en = ""
    res = ""

    try:
        path_zh = draw_bar(res_zh, font_path, useremail, "zh")
        res += "该领域下出现频率最多的20个关键词以及频率为： \n"
        for i in range(20):
            res += str(res_zh[i][0]) + ':' + str(res_zh[i][1]) + '\n'
    except:
        pass
    try:
        path_en = draw_bar(res_en, font_path, useremail, "en")
        res += "The 20 most frequently occurring keywords in this field and their frequency are: \n"
        for i in range(20):
            res += str(res_en[i][0]) + ':' + str(res_en[i][1]) + '\n'
    except:
        pass

    return {"path_zh": path_zh, "path_en": path_en, "res": res}

def show_keywords(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    query: str = Body(..., description="", example="")
    ):
    directory_path = '/root/bbft/ChatPaper/export/'

    user_exist_articles = [row[0] for row in list_articles(useremail, query)['gcarticles']]

    #print(user_exist_articles)
    subdirectories = []
    for item in user_exist_articles:
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
        else:
            subdirectories.append(item_path[:-1])

    _, _, res_zh, res_en = get_all_keyword_list_and_generate_wordclouds(subdirectories, useremail)

    first_keywords = [item[0] for item in res_en[:20]]
    return {"res_en": first_keywords}


def show_keywords_timeline(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    query: str = Body(..., description="", example="")
    ):
    directory_path = '/root/bbft/ChatPaper/export/'

    user_exist_articles = [row[0] for row in list_articles(useremail, query)['gcarticles']]

    #print(user_exist_articles)
    subdirectories = []
    for item in user_exist_articles:
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
        else:
            subdirectories.append(item_path[:-1])

    md_files_info = []
    
    for file_name in subdirectories:
        file_path = file_name + '/md.md'
        with open(file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
            time, keywords = extract_info_from_md(md_content)
            md_files_info.append((time, keywords))

    # 按照相同时间合并关键字列表
    merged_keywords = merge_keywords_by_time(md_files_info)

    # 按照时间排序的有序字典
    sorted_merged_keywords = OrderedDict(sorted(merged_keywords.items(), key=lambda x: x[0]))

    # 移除时间为空的项
    cleaned_sorted_merged_keywords = remove_empty_time_entries(sorted_merged_keywords)

    # 按照中文和英文分类关键字
    chinese_keywords, english_keywords = categorize_keywords(cleaned_sorted_merged_keywords)

    # 提取所有关键字并合并统计频次
    all_keywords = [keyword for keywords in chinese_keywords.values() for keyword in keywords]
    keyword_frequency_zh = merge_and_count_elements(all_keywords)[:20]
        
    # 提取所有关键字并合并统计频次
    all_keywords = [keyword for keywords in english_keywords.values() for keyword in keywords]
    keyword_frequency_en = merge_and_count_elements(all_keywords)[:20]

    # 获取关键字-时间字典
    key_time_dict_zh, time_line_zh = time_key_to_key_time(chinese_keywords)
    key_time_dict_en, time_line_en = time_key_to_key_time(english_keywords)

    current_path = os.getcwd()
    font_path = current_path + '/SimHei.ttf'

    path_zh = ""
    path_en = ""
    res = ""

    try:
        path_zh, res_zh = draw_key_timeline(keyword_frequency_zh, key_time_dict_zh, time_line_zh, font_path, useremail, "zh")
        res += "该领域下出现频率最多的20个关键词以及首次出现时间为： \n"
        for i in range(20):
            res += str(res_zh[i][0]) + ':' + str(res_zh[i][1][0]) + '\n'
    except:
        pass
    try:
        path_en, res_en = draw_key_timeline(keyword_frequency_en, key_time_dict_en, time_line_en, font_path, useremail, "en")
        res += "The 20 most frequently occurring keywords and their first appearance in this field are: \n"
        for i in range(20):
            res += str(res_en[i][0]) + ':' + str(res_en[i][1][0]) + '\n'
    except:
        pass

    return {"path_zh": path_zh, "path_en": path_en, "res": res}

def spend_money(
    amount: str = Body(..., description="amount", example="20"),
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com")
    ):
    if int(amount) < 0:
        return {"res": "fail"}
    db = Database(**config)
    select_all = db.select_all(field = "money", table_name = "user_basics WHERE email='"+useremail+"'")
    print("------------------------------------")
    print(select_all[0][0])
    db.update("user_basics", {"money": select_all[0][0] - int(amount)}, "email='"+useremail+"'")

    return {"res": "success"}

def query_money(
    useremail: str = Body(..., description="useremail", example="nxyqdl@163.com"),
    x: str = Body(..., description="", example="")
    ):
    db = Database(**config)
    select_all = db.select_all(field = "money", table_name = "user_basics WHERE email='"+useremail+"'")

    return {"res": select_all[0][0]}

def get_image_from_file(
    filename: str = Body(..., description="path", example="/root/bbft/ChatPaper/literatureReview/nxyqdl@163.com/wordcloud_zh.png"),
    x: str = Body(..., description="", example="")
    ):
    from fastapi.responses import StreamingResponse
  
    image_path = filename
    def stream_image():
        with open(image_path, "rb") as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(stream_image(), media_type="image/png")

def chat_llm(
    prompt: str = Body(..., description="", example=""),
    model: str = Body(..., description="", example="")
    ):
    openai.api_base = "https://api.openai.com/v1"
    openai.proxy = "http://127.0.0.1:7890"
    openai.api_key = OPENAI_API_KEY

    res = chat(prompt)


    return {"res": res}

################################
# 论文框架
################################

class LiteratureReview:
    def __init__(self, area, useremail, query, keyword, selectmethod):
        self.area = area
        self.username = useremail
        self.query = query
        self.keyword = keyword
        self.selectmethod = selectmethod


    def category(self, username, query, model):
        category_prompt = """Please categorize the following keywords.
        Merge similar keywords in each category.
        Just provide the category and keywords without any explanation, and wrap the categories in<category>.
        Here is an example:
        <Brain-Computer Interfaces> Brain computer interface, EEG
        <Deep Learning> Deep Learning, Machine learning, Convolutional Neural Networks, Transfer Learning, CNNs 
        <Classification> Classification, Common Spatial Patterns, P300, SSVEP, Event-related potential, MI 

        Here is the keywords:
        <keywords>
        {keywords}"""

        info_list = show_keywords(username, query)["res_en"]
        info = ""
        for key in info_list:
            info += key + ","
        info = info[:-1]

        category_prompt = category_prompt.format(keywords=info)

        
        if model == "spark":
            res = SparkCreate(category_prompt)
        else:
            category_res = chat_llm(category_prompt, None)
            res = category_res["res"]

        print("================================")
        print(res)
        pattern = r'<(.*?)>(.*?)'
        matches = re.findall(pattern, str(res), re.DOTALL)

        # 创建一个字典来存储键值对
        data_dict = defaultdict(list)

        for key, value in matches:
            print(key)
            print(value)
            # 将值拆分成单词，并去除空格
            words = [word.strip() for word in value.split(',')]
            
            # 将每个单词添加到对应键的值列表中
            data_dict[key] += words
        print(data_dict)
        return data_dict

    def summary_of_sections(self, username, query, keyword, selectmethod):
        # 目标URL
        url = 'http://119.3.238.159:8010/v1/summarykey'  # 替换成您要访问的实际URL

        # 请求数据，通常是一个字典或JSON格式数据
        data = {
            'useremail': username,
            'query': query,
            'keyword': keyword,
            'selectmethod': selectmethod
        }

        # 发送POST请求
        response = requests.post(url, json=data)

        if response.status_code == 200:
            # 请求成功，处理响应数据
            #print(json.loads(response.text)['res'])
            return json.loads(response.text)['res']
        else:
            # 请求失败，打印错误信息
            print(f"Request failed with status code {response.status_code}")
            print(response.text)

    def summary_num_of_publication_per_year(self, username, query, model):

        summary_prompt = """Please summarize the changes in the number of papers in the {area} field over time based on the following information. 
        Please respond in academic language as part of the paper. 
        No title required, just provide a paragraph of no more than 200 words:
        {info}"""
        info = show_num_of_publication_per_year(username, query)
        img_path = info["path"]
        info = info["res"]
        summary_prompt = summary_prompt.format(area = self.area, info=info)
        if model == "spark":
            return summary_prompt, img_path
        summary_res = chat_llm(summary_prompt, None)
        res = summary_res["res"]

        return res, img_path

    def summary_key_frequency(self, username, query, model):

        summary_prompt = """Please summarize the research hotspots in the {area} field based on the keyword frequency information below. 
        These keywords are summarized from Arxiv website in the {area} field:
        {info}"""
        info = show_keywords_frequency_bar(username, query)
        print("sssssssssssssssssssss")
        img_path = info["path_en"]
        info = info["res"]
        print(info)

        target_sentence = "The 20 most frequently occurring keywords in this field and their frequency are:"

        # 使用正则表达式匹配目标句子及其之后的内容
        # match = re.search(re.escape(target_sentence) + r".*?(?:[。]|$)", info)
        match = re.search(r''+target_sentence+'(.*?)$', info, re.DOTALL)
        #print(match)

        if match:
            result = match.group(0)
        else:
            result = "error"

        info = result
        summary_prompt = summary_prompt.format(area = self.area, info=info)
        if model == "spark":
            return summary_prompt, img_path
        summary_res = chat_llm(summary_prompt, None)
        res = summary_res["res"]

        return res, img_path

    def summary_timeline(self, username, query, model):
        summary_prompt = """Please summarize the development trends of technology in the {area} field based on the time nodes when the following keywords first appeared in the paper. 
        These keywords are summarized from all papers on the Arxiv website in the {area} field:
        {info}"""
        info = show_keywords_timeline(username, query)
        img_path = info["path_en"]
        info = info["res"]

        target_sentence = "The 20 most frequently occurring keywords and their first appearance in this field are:"

        # 使用正则表达式匹配目标句子及其之后的内容
        #match = re.search(re.escape(target_sentence) + r".*?(?:[。]|$)", info)
        match = re.search(r''+target_sentence+'(.*?)$', info, re.DOTALL)

        if match:
            result = match.group(0)
        else:
            result = "error"

        info = result
        summary_prompt = summary_prompt.format(area = self.area, info=info)
        if model == "spark":
            return summary_prompt, img_path
        summary_res = chat_llm(summary_prompt, None)
        res = summary_res["res"]

        return res, img_path

    def introduction_conclusion(self, username, query, model):
        introduction_prompt = """Please write an introduction to the literature review in the {area} field. 
        This review summarizes the first appearance time, frequency, and corresponding technical papers of the following keywords, 
        selected from all papers in this field on the Arxiv website:
        {info}"""

        conclusion_prompt = """Please write a summary of the literature review in the {area} field and describe future directions. 
        This review summarizes the first appearance time, frequency, and corresponding technical papers of the following keywords, 
        selected from all papers in this field on the Arxiv website:
        {info}"""

        info_list = show_keywords(username, query)["res_en"]
        info = ""
        for key in info_list:
            info += key + ","
        info = info[:-1]

        introduction_prompt = introduction_prompt.format(area = self.area, info=info)
        conclusion_prompt = conclusion_prompt.format(area = self.area, info=info)
        if model == "spark":
            print("#####################################")
            print("introduction_prompt:")
            print("#####################################")
            print(introduction_prompt)
            print("#####################################")
            print("conclusion_prompt")
            print("#####################################")
            print(conclusion_prompt)
            return introduction_prompt, conclusion_prompt
        introduction_res = chat_llm(introduction_prompt, None)
        introduction_res = introduction_res["res"]

        conclusion_res = chat_llm(conclusion_prompt, None)
        conclusion_res = conclusion_res["res"]

        return introduction_res, conclusion_res

    def generate_article(self):
        current_datetime = datetime.datetime.now()
        folder_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        target_directory = "/var/www/html/temp/" + self.username + "/" + folder_name
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        htmls = []
        introduction_res, conclusion_res = self.introduction_conclusion(self.username, self.query, None)
        htmls.append('# A Literature Review of ' + self.query)
        htmls.append('\n\n\n')
        htmls.append('## 1 Introduction')
        htmls.append('\n')
        htmls.append(introduction_res)
        htmls.append('\n')
        res, img_path = self.summary_num_of_publication_per_year(self.username, self.query, None)
        shutil.copy2(img_path, target_directory)
        htmls.append('![](http://119.3.238.159/temp/' + folder_name +'/' + img_path.split('/')[-1] + ')')
        htmls.append('\n')
        htmls.append(res)
        htmls.append('\n')
        res, img_path = self.summary_key_frequency(self.username, self.query, None)
        shutil.copy2(img_path, target_directory)
        htmls.append('![](http://119.3.238.159/temp/' + folder_name +'/' + img_path.split('/')[-1] + ')')
        htmls.append('\n')
        htmls.append(res)
        htmls.append('\n')
        res, img_path = self.summary_timeline(self.username, self.query, None)
        shutil.copy2(img_path, target_directory)
        htmls.append('![](http://119.3.238.159/temp/' + folder_name +'/' + img_path.split('/')[-1] + ')')
        htmls.append('\n')
        htmls.append(res)
        htmls.append('\n')
        data_dict = self.category(self.username, self.query)
        categories = ''
        for i in data_dict.keys():
            categories += i + ', '
        htmls.append('In this article, we categorize all keywords into ' 
        + str(len(data_dict.keys())) + ' categories, namely: ' + categories[:-2]
        + '. The following will elaborate on these ' + str(len(data_dict.keys())) 
        + ' categories separately.')
        num = 2
        for i in data_dict.keys():
            htmls.append('## ' + str(num) + ' ' + i)
            htmls.append('\n')
            sub_num = 1
            for keyword in data_dict[i]:
                htmls.append('### ' + str(num) + '.' + str(sub_num) + ' ' + keyword)
                htmls.append('\n')
                res = self.summary_of_sections(self.username, self.query, self.keyword, self.selectmethod)
                htmls.append(res)
                htmls.append('\n')
                sub_num += 1
            num += 1
        htmls.append('## ' + str(num) + ' Conclusion')
        htmls.append('\n')
        htmls.append(conclusion_res)
        file_name = target_directory + '/md.md'
        with open(file_name, 'w', encoding="utf-8") as f:
            # 将html格式的内容写入文件
            f.write("\n".join(htmls))

        return file_name

        
def generate_article(
    useremail: str = Body(..., description="", example=""),
    query: str = Body(..., description="", example=""),
    keyword: str = Body(..., description="", example=""),
    selectmethod: str = Body(..., description="", example="")
    ):
    literatureReview = LiteratureReview(query, useremail, query, keyword, selectmethod)
    res = literatureReview.generate_article()

    return {"res": res}

async def literature_review_ws(websocket: WebSocket):
    await websocket.accept()
    import SparkApi
    import SparkWS
    query = websocket.query_params.get("query")
    useremail = websocket.query_params.get("useremail")
    keyword = websocket.query_params.get("keyword")
    selectmethod = websocket.query_params.get("selectmethod")
    language = "zh"
    SparkApi.websocket_clients = [websocket]
    literatureReview = LiteratureReview(query, useremail, query, keyword, selectmethod)
    current_datetime = datetime.datetime.now()
    folder_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    target_directory = "/var/www/html/temp/" + useremail + "/" + folder_name
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    htmls = []
    
    try:
        while True:
            # 这里可以添加与前端交互的逻辑
            question = await websocket.receive_text()
            # 处理从前端接收到的数据
            if language == "zh":
                await websocket.send_text('# 关于 ' + query + ' 领域下的综述')
            else:
                await websocket.send_text('# A Literature Review of ' + query)
            await websocket.send_text('\n')
            if language == "zh":
                await websocket.send_text('## 1 介绍')
            else:
                await websocket.send_text('## 1 Introduction')
            await websocket.send_text('\n')
            SparkApi.answer =""
            prompt, conclusion_prompt = literatureReview.introduction_conclusion(literatureReview.username, literatureReview.query, "spark")
            if language == "zh":
                prompt = "请用中文回答下述问题：" + prompt
                conclusion_prompt = "请用中文回答下述问题：" + conclusion_prompt
            question = [{'role': 'user', 'content': prompt}]
            print(prompt)
            await SparkApi.main(SparkWS.appid,SparkWS.api_key,SparkWS.api_secret,SparkWS.Spark_url,SparkWS.domain,question)
            await websocket.send_text('\n')

            prompt, img_path = literatureReview.summary_num_of_publication_per_year(literatureReview.username, literatureReview.query, "spark")
            shutil.copy2(img_path, target_directory)

            imgsrc = 'http://119.3.238.159/temp/' + useremail +'/' + folder_name + '/' + img_path.split('/')[-1]
            await websocket.send_text('\n')
            await websocket.send_text('![]('+imgsrc+')')
            # await websocket.send_text('<img src=" '+imgsrc+' " alt="Remote Image">')
            await websocket.send_text('\n')
            if language == "zh":
                prompt = "请用中文回答下述问题：" + prompt
            question = [{'role': 'user', 'content': prompt}]
            print(prompt)
            await SparkApi.main(SparkWS.appid,SparkWS.api_key,SparkWS.api_secret,SparkWS.Spark_url,SparkWS.domain,question)
            await websocket.send_text('\n')

            prompt, img_path = literatureReview.summary_key_frequency(literatureReview.username, literatureReview.query, "spark")
            shutil.copy2(img_path, target_directory)
            imgsrc = 'http://119.3.238.159/temp/' + useremail +'/' + folder_name + '/' + img_path.split('/')[-1]
            await websocket.send_text('\n')
            await websocket.send_text('![]('+imgsrc+')')
            await websocket.send_text('\n')
            if language == "zh":
                prompt = "请用中文回答下述问题：" + prompt
            question = [{'role': 'user', 'content': prompt}]
            print(prompt)
            await SparkApi.main(SparkWS.appid,SparkWS.api_key,SparkWS.api_secret,SparkWS.Spark_url,SparkWS.domain,question)
            await websocket.send_text('\n')

            prompt, img_path = literatureReview.summary_timeline(literatureReview.username, literatureReview.query, "spark")
            shutil.copy2(img_path, target_directory)
            imgsrc = 'http://119.3.238.159/temp/' + useremail +'/' + folder_name + '/' + img_path.split('/')[-1]
            await websocket.send_text('\n')
            await websocket.send_text('![]('+imgsrc+')')
            await websocket.send_text('\n')
            if language == "zh":
                prompt = "请用中文回答下述问题：" + prompt
            question = [{'role': 'user', 'content': prompt}]
            print(prompt)
            await SparkApi.main(SparkWS.appid,SparkWS.api_key,SparkWS.api_secret,SparkWS.Spark_url,SparkWS.domain,question)
            await websocket.send_text('\n')

            data_dict = literatureReview.category(literatureReview.username, literatureReview.query, "spark")
            categories = ''
            for i in data_dict.keys():
                categories += i + ', '
            await websocket.send_text('\n')
            if language == "zh":
                await websocket.send_text('在本文中，我们将所有关键词分为 '
                + str(len(data_dict.keys())) + ' 类， 分别是： ' + categories[:-2]
                + '。 接下来对这 ' + str(len(data_dict.keys())) 
                + ' 类进行分别概述。')
                await websocket.send_text('\n')
            else:
                await websocket.send_text('In this article, we categorize all keywords into '
                + str(len(data_dict.keys())) + ' categories, namely: ' + categories[:-2]
                + '. The following will elaborate on these ' + str(len(data_dict.keys())) 
                + ' categories separately.')
                await websocket.send_text('\n')
            num = 2

            await websocket.send_text('## ' + str(num) + ' Conclusion')
            await websocket.send_text('\n')
            question = [{'role': 'user', 'content': conclusion_prompt}]
            print(prompt)
            await SparkApi.main(SparkWS.appid,SparkWS.api_key,SparkWS.api_secret,SparkWS.Spark_url,SparkWS.domain,question)
            await websocket.send_text('\n')

            
            await websocket.close()
    except:
        pass

def spark_agent(
    useremail: str = Body(..., description="", example=""),
    userinput: str = Body(..., description="", example="")
    ):
    prompt = """请判断下方<user></user>中用户输入的提问语句<input>能否归类到如下5类功能。如果可以归类则返回。否则不要返回：
    1. 领域文章每年数量
    2. 词云图生成
    3. 关键词频率直方图
    4. 关键词首次出现时间及随时间累积频率
    5. 领域综述生成

    同时请判断用户提问的领域是否在<user></user>中的<field>中给出的领域，中英文均可。如果是则返回一条<field>包裹对应结果，否则不要返回

    下面是一个问题样例：
    <example>
    <input>请帮我总结人工智能领域下的论文</input>
    <field>YY</field>
    <field>XX</field>
    <field>BCI</field>
    <field>AI</field>

    则返回结果应为:
    <category>领域综述生成</category>
    <field>AI</field>
    </example>

    下面是本次提问的信息：
    <user>
    <input>{userinput}</input>
    {field}
    </user>
    """
    res = list_query_category(useremail, None)["res"]
    res_text =""
    fields = []
    for i in res:
        res_text += "<field>" + i[0] + "</field> \n  "
        fields.append(i[0])
    prompt = prompt.format(userinput=userinput, field=res_text)
    print(prompt)

    text = SparkCreate(prompt)
    print(text)
    category_match = re.findall(r'<category>(.*?)</category>', text)
    field_match = re.findall(r'<field>(.*?)</field>', text)
    category_text = ''
    field_text = ''
    if category_match and len(category_match) == 1:
        category_text = category_match[0].strip()
        print("Category:", category_text)

    if field_match and len(field_match) == 1:
        field_text = field_match[0].strip()
        print("Field:", field_text)

    success = 0
    if category_text in ['领域文章每年数量','词云图生成','关键词频率直方图','关键词首次出现时间及随时间累积频率','领域综述生成']:
        success += 1
    if field_text in fields:
        success += 1

    return {"category": category_text, "field": field_text, "success": success}

def search_summary_result(
    useremail: str = Body(..., description="", example=""),
    x: str = Body(..., description="", example="")
):
    # 指定要搜索的根文件夹路径
    root_folder = "/var/www/html/temp/"  # + useremail

    # 初始化一个空的字典列表
    result_list = []

    # 遍历根文件夹及其子文件夹
    for folder_path, _, files in os.walk(root_folder):
        for file in files:
            # 检查文件扩展名是否为.md（不区分大小写）
            if file.lower().endswith('.md'):
                file_path = os.path.join(folder_path, file)
                
                # 打开MD文件并读取第一行信息
                with open(file_path, 'r', encoding='utf-8') as md_file:
                    first_line = md_file.readline().strip()[2:]
                    
                    # 添加到字典列表中
                    result_list.append({'key': first_line, 'value': file_path})

    return {"res": result_list}

if __name__ == '__main__':

    import pymysql
    import SparkWS

    connection = pymysql.connect(
        host='localhost',     # 主机名
        user='root',      # 用户名
        password='root',  # 密码
        database='bbft'   # 数据库名
    )
    
    cursor = connection.cursor()
    
    create_table_query = """
        CREATE TABLE IF NOT EXISTS gcarticles (
        name VARCHAR(255),
        path VARCHAR(255),
        submitted INT,
        query VARCHAR(255),
        keyword VARCHAR(255),
        translated INT,
        useremail VARCHAR(255)

    ) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """

    cursor.execute(create_table_query)
    connection.commit()
    
    # 设置连接数据库的参数
    config = {
        "host": "127.0.0.1",
        "port": 3306,
        "database": "bbft",
        "charset": "utf8",
        "user": "root",
        "passwd": "root"
    }


    # import time
    
    app = FastAPI()
    app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )
    #app.post("/v1/chatglmarxiv", response_model="")(chat_arxiv_main(args=arxiv_args))
    app.post("/v1/chatglmarxiv", response_model="")(chat_arxiv_main)
    app.post("/v1/readmd", response_model="")(read_md)
    app.post("/v1/listarticles", response_model="")(list_articles)
    app.post("/v1/downloadfile", response_model="")(download_file)
    app.post("/v1/getimage", response_model="")(get_image)
    app.post("/v1/countarticles", response_model="")(count_articles)
    app.post("/v1/updatearticle", response_model="")(update_articles)
    app.post("/v1/deleteredundance", response_model="")(delete_redundance)
    app.post("/v1/updatedatabase", response_model="")(update_database)
    app.post("/v1/updatedatabasepath", response_model="")(update_database_path)
    app.post("/v1/sparktranslate", response_model="")(spark_translate)
    app.post("/v1/searchsparktranslate", response_model="")(search_spark_translate)

    # 文献综述相关
    app.post("/v1/showwordcloud", response_model="")(show_wordcloud)
    app.post("/v1/listquerycategory", response_model="")(list_query_category)
    app.post("/v1/getimagefromfile", response_model="")(get_image_from_file)
    app.post("/v1/shownumofpublicationperyear", response_model="")(show_num_of_publication_per_year)
    app.post("/v1/showkeywordsfrequencybar", response_model="")(show_keywords_frequency_bar)
    app.post("/v1/showkeywordstimeline", response_model="")(show_keywords_timeline)
    app.post("/v1/showkeywords", response_model="")(show_keywords)
    app.post("/v1/spendmoney", response_model="")(spend_money)
    app.post("/v1/querymoney", response_model="")(query_money)
    app.post("/v1/chatllm", response_model="")(chat_llm)
    app.post("/v1/generatearticle", response_model="")(generate_article)
    app.post("/v1/searchsummaryresult", response_model="")(search_summary_result)
    app.post("/v1/sparkagent", response_model="")(spark_agent)
    app.websocket("/ws")(SparkWS.websocket_endpoint)
    app.websocket("/ws/literature")(literature_review_ws)
    uvicorn.run(app, host="0.0.0.0", port=8008)

    #start_time = time.time()
    #chat_arxiv_main(args=arxiv_args)
    #print("summary time:", time.time() - start_time)
