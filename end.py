import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

# 构造UA头
headers = {
    "Accept-Encoding": "Gzip",  # 使访问速度更快
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
}


# 获取城市字典的方法
def get_city():
    url = 'https://www.fang.com/SoufunFamily.htm'
    result = requests.get(url, headers=headers)
    result.encoding = 'UTF-8'  # 对返回结果进行编码
    tree = etree.HTML(result.text)  # html解析
    # 创建城市名列表和城市代号列表
    city_list = []
    city_english_list = []

    # 爬取城市列表
    for i in range(1, 10):
        city_list.extend(tree.xpath(f"//tr[@id='sffamily_B03_0{i}']//a/text()"))
    for i2 in range(10, 31):
        city_list.extend(tree.xpath(f"//tr[@id='sffamily_B03_{i2}']//a/text()"))

    # 爬取城市对应url列表
    for j in range(1, 10):
        city_english_list.extend(tree.xpath(f"//tr[@id='sffamily_B03_0{j}']//a/@href"))
    for j2 in range(10, 31):
        city_english_list.extend(tree.xpath(f"//tr[@id='sffamily_B03_{j2}']//a/@href"))
    city_english_list = [s[8:-10] for s in city_english_list]  # 列表推导式截取特定代码

    keys = city_list  # 将城市名列表转为元组作为字典的键
    values = city_english_list  # 将城市代号作为对应的值
    city_dict = dict(zip(keys, values))  # 利用zip进行迭代转为字典

    return city_dict


# 爬取对应城市购房信息的方法
def get_html(url):
    # 初始化房屋列表
    houses_info = []
    # 选择购买新房的情况
    if style == 1:
        # 初始化联系方式，单价，总价列表
        room_phones = []
        unit_prices = []
        sum_prices = []
        for i in range(1, 8):  # 可以选择访问多少页面
            urls = "https://{}.newhouse.fang.com/house/s/b9{}".format(url, i)
            result = requests.get(urls, headers=headers)
            tree = etree.HTML(result.text)  # 解析html
            # 爬取并处理楼房信息
            for item1 in range(21, 30):  # 通过特定构造获取相关信息
                house_info = {
                    '名称': tree.xpath('normalize-space(//div[@id="sjina_C{}_09"]/@data-title)'.format(item1)),
                    '户型': tree.xpath('//div[@class="house_type clearfix" and @id="sjina_C{}_04"]/a/text()'.format(item1)),
                    '面积': tree.xpath('//div[@class="house_type clearfix" and @id="sjina_C{}_04"]/text()[last()]'.format(item1)),
                    '地址': tree.xpath('//div[@class="address" and @id="sjina_C{}_06"]/a/text()'.format(item1)),
                    '描述': tree.xpath('//div[@class="fangyuan" and @id="sjina_C{}_07"]/a/text()'.format(item1))}
                houses_info.append(house_info)
            # 因为联系方式、单价和总价没有特定编号，单独爬取并处理联系方式、单价和总价
            room_phone = tree.xpath('//div[@class="tel"]/p/text()')
            # 判断是否返回，如果为空，则赋值为NULL
            if not room_phone:
                room_phone = ["NULL"]
            else:
                room_phone = [phone.strip() for phone in room_phone]
            room_phones.extend(room_phone)  # 将联系方式加入列表
            unit_price = tree.xpath('//div[@class="nhouse_price"]/span/text()')              # 获取单价
            if not unit_price:
                unit_price = ["NULL"]
            else:
                unit_price = [price.strip() for price in unit_price]
            unit_prices.extend(unit_price)
            # 获取总价
            sum_price = tree.xpath('//p[@class="zj_price"]/text()')
            if not sum_price:
                sum_price = ["NULL"]
            else:
                sum_price = [price.strip() for price in sum_price]
            sum_prices.extend(sum_price)
        # 将联系方式、单价和总价添加到houses_info的每个字典中
        j = 0
        j2 = 0
        # 将联系方式，单价，总价等信息存入字典
        for house_info in houses_info:
            if j < len(room_phones) - 1:
                number = f'{room_phones[j]}转{room_phones[j + 1]}'
                house_info['联系方式'] = number
                j += 2
            if j2 < len(unit_prices) and j2 < len(sum_prices):
                house_info['单价'] = unit_prices[j2]
                house_info['总价'] = sum_prices[j2]
                j2 += 1
        print(houses_info)

    elif style == 2:
        driver = webdriver.Edge()  # 初始化浏览器
        # 爬取特定数量web页面
        for i in range(1, 3):
            # 目标网址
            urls = "https://{0}.esf.fang.com/house/i3{1}/".format(url, i)  # 替换为你要爬取的网页地址
            driver.get(urls)
            time.sleep(5)  # 等待页面加载完成
            names2 = driver.find_elements(By.XPATH, '//h4[@class="clearfix"]/a/span[@class="tit_shop"]')  # 爬取房屋名字
            room_type = driver.find_elements(By.XPATH, '//p[@class="tel_shop"]')  # 爬取房屋其他信息
            sum_prices = driver.find_elements(By.XPATH, '//dd[@class="price_right"]/span[@class="red"]/b')  # 爬取总价
            unit_prices = driver.find_elements(By.XPATH, '//dd[@class="price_right"]/span[not(@class)]')  # 爬取单价
            address = driver.find_elements(By.XPATH, "//p[@class='add_shop']")  # 爬取地址
            # 将房屋信息插入信息字典
            lots = len(names2)
            for item2 in range(0, lots):
                house_info = {
                    '房屋名称': names2[item2].text,
                    '房屋综合信息': room_type[item2].text,
                    '单价': unit_prices[item2].text,
                    '总价': sum_prices[item2].text + '万元',
                    '地址': f'{address[item2].text}'
                }
                houses_info.append(house_info)
        # 关闭浏览器
        driver.quit()
    else:
        # 初始化浏览器
        driver = webdriver.Edge()
        for i in range(1, 3):
            # 打开网页
            urls = "https://{}.zu.fang.com/house/i3{}".format(url, i)
            driver.get(urls)
            time.sleep(5)
            names3 = driver.find_elements(By.XPATH, '//p[@class="title" and contains(@id, "rentid_D09")]/a')  # 爬取房源名
            other_information = driver.find_elements(By.XPATH, '//p[@class="font15 mt12 bold"]')  # 爬取房屋综合信息
            unit_price = driver.find_elements(By.XPATH,"//div[@class='moreInfo']/p[@class='mt5 alingC']/span[@class='price']")  # 爬取房租
            address = driver.find_elements(By.XPATH, "//p[@class='gray6 mt12']//a")  # 爬取房租
            for item3 in range(0, len(names3)):
                house_info = {
                    '房屋名称': names3[item3].text,
                    '房屋综合信息': other_information[item3].text,
                    '房租（单位：元/月）': unit_price[item3].text,
                    '地址': ''
                }
                address_start = item3 * 3
                # 检查地址列表是否有足够的元素来组成一个完整的地址
                if address_start + 2 < len(address):
                    house_info['地址'] = f'{address[address_start].text}-{address[address_start + 1].text}-{address[address_start + 2].text}'
                houses_info.append(house_info)
        driver.quit()
    # 将爬取下来的信息写入文件
    save_to_file(houses_info)


# 将爬取房屋相关信息写入文件
def save_to_file(data, filename='house_zu_information.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


# 输入需要爬取的城市
style = int(input("请输入您想要购买的房型：（购买新房输入1，二手房输入2，租房输入3）\n"))
city = input('请输入您需要的城市：\n')
city_dicts = get_city()
city_url = city_dicts[city]  # 通过字典获取对应代号
print(city_url)
get_html(city_url)  # 调用方法
