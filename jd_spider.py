import os

import requests
from bs4 import BeautifulSoup
import re
import xlwt
import os
import pandas as pd

item_name = input('请输入商品名：')


# 下载图片函数
# def down_pic(down_url, picname):
#     '''
#     下载图片函数
#     :param down_url: 下载地址
#     :param picname: 保存的图片名字
#     :return:
#     '''


#     header = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0'
#     }

#     req = requests.get(url=down_url, headers=header)
#     req.encoding = 'utf-8'

#     with open('%s' % picname, "wb") as f:  # 开始写文件，wb代表写二进制文件
#         f.write(req.content)

def gethttptext(url):
    try:

        kv = {
            # 自己获取cookie
            'cookie': '__jdu=16318419670871277957373; shshshfpa=c523550f-aeee-f59e-fd6f-48722c5502a5-1631841968; shshshfpb=i%2Fe0tVL3WaFkx%2FnUswZYa6Q%3D%3D; __jdv=76161171|www.google.com|-|referral|-|1642131155953; areaId=17; qrsc=3; rkv=1.0; ipLoc-djd=17-1381-50712-50817; __jda=122270672.16318419670871277957373.1631841967.1642131156.1642987987.3; __jdb=122270672.11.16318419670871277957373|3.1642987987; __jdc=122270672; shshshfp=0c51e9d6647b98ef1fce7733142e0dd5; shshshsID=8a2011caddc509c29ba26e379221e758_11_1642988786322; 3AB9D23F7A4B3C9B=EYZ7DBGM65U2SXBIGM74KNEU3FPJRI243747VEE45UJOOEANTE77V6XCTFHKUUEGF5TYFLSGUBR5JHUNGVPLCI7U7U',
            'user-agent': 'Mozilla/5.0'
        }
        r = requests.get(url, headers=kv, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print("提取失败", e)
        return ""


# 爬取京东中篮球数据
def jingdong_spider():
    global item_name

    # 列表存储ID,标题,价格,图片url
    item_list = []

    # 防止过多爬取被屏蔽，抓取前十页内容
    for i in range(0, 15):

        # 列表存储ID,标题,价格,图片url
        # item_list = []

        url = "https://search.jd.com/Search?keyword=" + item_name + "&qrst=1&stock=1&pvid=d038ffe9573b4bf58a4ea5ed68450047&page=" + str(
            2 * i + 1) + "&click=0"

        page_html = gethttptext(url)

        # 直接提取
        # soup = BeautifulSoup(page_html, 'lxml')  # lxml为解析器
        soup = BeautifulSoup(page_html, 'html.parser')
        # print(soup)

        data_list = soup.findAll(name="li", attrs={"class": "gl-item"})

        # print(data_list)

        for item in data_list:

            # soup_li = BeautifulSoup(item, 'lxml')

            # 去除换行符

            # print(item)

            item = str(item).replace('\n', '')

            # print(item)

            # 使用正则表达式提取ID
            jd_id = re.findall(r'strong class="J_(.+?)" ', item)

            jd_id = jd_id[0]
            # print(jd_id)
            goods_url = "https://item.jd.com/" + str(jd_id) + ".html"
            goods_html = gethttptext(goods_url)
            goods_soup = BeautifulSoup(goods_html, 'html.parser')
            goods_item = str(goods_soup).replace('\n', '')
            print(jd_id)
            jd_name = re.findall(r'<div class="sku-name"' + '(.+?)' + '</div>', goods_item)
            if jd_name:
                if jd_name[0]:
                    if '</img>' in jd_name[0]:
                        jd_name = re.findall(r'">' + '(.+?)' + '</img>', jd_name[0])[0].strip()
                    else:
                        jd_name = re.findall(r'>(.+)', jd_name[0])[0].strip()
                else:
                    jd_name = ''
            else:
                jd_name = ''
            # 使用正则表达式提取价格
            jd_price = re.findall(r'data-price="' + jd_id + '">(.+?)</i>', item)[0]

            # 提取店铺名
            jd_shop = re.findall(r'<div class="p-shop"' + '(.+?)' + '</div>', item)[0]
            jd_shop = re.findall(r'title="(.+?)">', jd_shop)[0]
            # print(jd_shop)
            # 提取评价数

            comment_url = "https://club.jd.com/comment/productCommentSummaries.action?" + "referenceIds=" + str(jd_id)
            comment_html = gethttptext(comment_url)
            comment_soup = BeautifulSoup(comment_html, 'html.parser')
            comment_soup = str(comment_soup).replace('\n', '')
            # 总评
            jd_allcomment = re.findall(r'"CommentCountStr":"' + '(.+?)' + '"', comment_soup)[0].replace('Íò', '万')

            # 好评
            jd_goodcomment = re.findall(r'"GoodCountStr":"' + '(.+?)' + '"', comment_soup)[0].replace('Íò', '万')

            # 中评
            jd_generalcomment = re.findall(r'"GeneralCountStr":"' + '(.+?)' + '"', comment_soup)[0].replace('Íò', '万')

            # 差评
            jd_poorcomment = re.findall(r'"PoorCountStr":"' + '(.+?)' + '"', comment_soup)[0].replace('Íò', '万')

            # jd_comment = re.findall(r'"商品评价'+'(.+?)'+'</s>', goods_item)
            # print(jd_comment)
            # jd_comment = re.findall(r'">(.+?)</a>', jd_comment)[0]
            # print(jd_comment)
            # 提取商品名
            #             ems = re.findall(r'<em>(.+?)</em>', item)

            #             for em in ems:

            #                 if '￥' not in em:

            #                     jd_name = em

            #             jd_name = jd_name.replace('<font class="skcolor_ljg">'+item_name+'</font>',item_name)\
            #                 .replace('<span class="p-tag" style="background-color:#c81623">京东超市</span>','')\
            #                 .replace('\t','')

            # 提取图片地址
            # jd_url = 'https:' + re.findall(r'data-lazy-img="(.+?)" ', item)[0]

            item_list.append(
                [jd_id, jd_name, jd_shop, jd_price, jd_allcomment, jd_goodcomment, jd_generalcomment, jd_poorcomment,
                 goods_url])

        # print(item_list[0])
    pd_data = pd.DataFrame(columns=['商品编号', '商品名称', '商铺名称', '价格', '总评论数', '好评数', '中评数', '差评数', '商品链接'], data=item_list)
    # pd_data = pd.DataFrame(data = item_list)
    pd_data.to_csv(r'D:/data.csv', mode='a', index=False)
    # print("共有商品：", len(item_list))


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 从京东爬取篮球商品函数
    jingdong_spider()

    # 从数据库中读取数据，比较价格，读取页面
    # # 插入数据库中，ID，名称，图片地址，价格
# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
