# -*- coding:utf-8 -*-
# Sina Blog Downloader
import sys
import os
import json
import urllib
from pyquery import PyQuery

urlopen = urllib.request.urlopen


def change_file_ext(filename, extname=""):
    """
    修改文件扩展名
    :param filename: 输入的文件路径名
    :param extname: 要更改分扩展名，如 .txt
    :return:
    """
    try:
        if extname[0] != ".":
            extname = "." + extname
    except:
        extname = ""

    if os.path.splitext(filename)[1] == "":
        uouttxt = filename + "." + extname
    elif os.path.splitext(filename)[1] == ".":
        uouttxt = filename + extname
    else:
        uouttxt = filename[:0 - len(os.path.splitext(filename)[1])] + extname
    return uouttxt


def ensure_dir(path):
    """
    确保目录存在,如果存在则忽略,没有则新建
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def print_progress_bar(percent, text_head="", text_tail=""):
    """
    显示终端进度条
    :param percent: int,百分比
    :param text_head: str,开头文字
    :param text_tail: str,尾部文字
    :return:
    """
    bar_length = 100
    hashes = "█" * int(percent / 100.0 * bar_length)
    spaces = "░" * (bar_length - len(hashes))
    sys.stdout.write("\r%s[%s] %d%% %s" % (text_head, hashes + spaces, percent, text_tail))
    sys.stdout.flush()


def replace_str(str_data, replace_dict):
    """
    替换字符串中指定的字符串
    :param str_data: str
    :param replace_dict: dict
    :return:
    """

    for key in replace_dict.keys():
        str_data = str_data.replace(key, replace_dict[key])

    return str_data


def get_articlelist(url, replace_dict=None):
    """
    获取列表页
    :param url:
    :param replace_dict:
    :return:
    """
    HTML = urlopen(url).read()  # 读取博客目录
    article_list = PyQuery(HTML)("div.articleList").html()

    try:
        article_list_link = PyQuery(article_list)("a")

        # 保存页面
        filename = url.split("/")[-1]
        HTML = replace_str(HTML.decode('utf-8'), replace_dict)
        with open(os.path.join(dir_html, filename), "w", encoding="utf-8") as f:
            f.write(HTML)

        for a in article_list_link.items():
            get_page(a.attr("href"), replace_dict=replace_dict)
    except Exception as err:
        if err:
            print("发生错误:", err)
        pass


def get_page(url, replace_dict=None):
    """
    获取网页
    :param url: 网页地址
    :param replace_dict: 替换网页内容的 dict
    :return:
    """
    HTML = urlopen(url).read()
    # 保存页面
    filename = url.split("/")[-1]
    HTML = replace_str(HTML.decode('utf-8'), replace_dict)
    with open(os.path.join(dir_html, filename), "w", encoding="utf-8") as f:
        global count_blog_downloaded
        print_progress_bar(count_blog_downloaded / count_blog * 100, "处理博客",
                           str(count_blog_downloaded) + "/" + str(count_blog) + "个")
        count_blog_downloaded += 1
        f.write(HTML)


# 程序开始
# 首页的替换字典
replace_dict_index = {
    "http://blog.sina.com.cn/s/": "html/"
}

# 列表页和详情页的替换字典
replace_dict = {
    "http://blog.sina.com.cn/s/": ""
}

map_articlelist = {}  # 分类的文章列表
count_page = 1  # 博客页面数量
count_blog_downloaded = 0  # 已下载的页面
root_path = os.path.abspath(os.path.dirname(__file__))  # 系统所在路径
file_conf = change_file_ext(sys.argv[0], ".cnf")  # 配置文件的路径

# 找不到配置文件的时候创建配置文件
if not os.path.exists(file_conf):
    with open(file_conf, "wb") as json_file:
        cnf_data = {"blog_ID": ""}  # 默认配置文件信息
        json.dump(cnf_data, json_file, ensure_ascii=False)
    raise ValueError("请在当前目录下的 cnf 文件中填写所需的新浪用户 ID")

# 读取配置文件
with open(file_conf, "r") as json_file:
    cnf_data = json.load(json_file)

# 检查是否设置了博客ID
blog_ID = cnf_data.get("ID", "")  # 新浪ID
if blog_ID.strip() == "":
    raise ValueError("未指定博客ID")

# 数据存储路径
dir_data = os.path.join(root_path, "data")  # 默认数据文件目录
dir_user_ID = os.path.join(dir_data, blog_ID)  # 指定用户ID的数据目录
dir_html = os.path.join(dir_user_ID, "html")  # 元数据目录
ensure_dir(dir_data)  # 确保目录存在
ensure_dir(dir_user_ID)
ensure_dir(dir_html)

blog_index_URL = "http://blog.sina.com.cn/s/articlelist_" + blog_ID + "_0_1.html"
page_index = urlopen(blog_index_URL).read()  # 读取博客目录
menu = PyQuery(page_index)("div.menuList").html()
menu_links = PyQuery(menu)("a")

# 记录分类
map_category = {}
for li in menu_links.items():
    text = li.text()
    if text != "博文收藏":  # 忽略博文收藏目录
        map_category[text] = li.attr("href")
len_map_category = len(map_category)

# 保存首页 HTML
HTML = replace_str(page_index.decode('utf-8'), replace_dict=replace_dict_index)
with open(os.path.join(dir_user_ID, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML)

# 分析记录数
paging = PyQuery(page_index)("ul.SG_pages").html()
if paging.strip() != "":
    count_page = int(PyQuery(paging)("span").text().replace(u"共", "").replace(u"页", ""))
HTML_paging = PyQuery(page_index)("div.SG_colW73").html()
HTML_paging = PyQuery(HTML_paging)("div.SG_connHead").html()
HTML_paging = PyQuery(HTML_paging)("span.title").html()
count_blog = int(PyQuery(HTML_paging)("em").text().replace(u"(", "").replace(u")", ""))

print("该博客一共", len_map_category, "个分类,博文总数：", count_blog)

# 遍历每个分类
for category_name in map_category.keys():
    category_URL = map_category[category_name]
    page_articlelist = urlopen(category_URL).read()  # 读取该分类下的博文列表

    # 分析页数
    count_page_category = 1
    HTML_paging = PyQuery(page_articlelist)("ul.SG_pages").html()
    if HTML_paging.strip() != "":
        count_page_category = int(PyQuery(HTML_paging)("span").text().replace(u"共", "").replace(u"页", ""))
    # 获取分类的所有分页
    count_page = 0
    while count_page < count_page_category:
        get_articlelist(category_URL, replace_dict=replace_dict)
        count_page += 1
