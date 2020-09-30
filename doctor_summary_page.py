 # -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 20:23:27 2020

@author: Jin Zhang
"""

import requests
import time
import csv
from lxml import etree


def save_data_header(header, save_path):
    with open(save_path, 'a', newline='',encoding='utf-8-sig') as f: 
        writer = csv.DictWriter(f,fieldnames=header) 
        writer.writeheader()
    
    
def save_data(data, header, save_path):
    with open(save_path, 'a', newline='',encoding='utf-8-sig') as f: 
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writerows(data) 


def get_page_html(url):
    """
    Input: the url of doctors' page
    Output unparsed html
    """
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    html = response.text
    status_code = response.status_code
    
    # If the status code is not 200, execute the following section
    # This section repeats the visit, increasing the time to sleep each time
    # Repeat 16 times at most
    count = 0
    while status_code != 200 and count < 16:
        response = requests.get(url=url,headers={'User-Agent': user_agent})

        html = response.text
        status_code = response.status_code
        print(status_code)
        
        count += 1
        time.sleep(count*0.1)
    return html


def get_doctor_info(html):
    """
    Input
    ------
    the unparsed html of the doctor
    
    Output
    ------
    Main interface data of coronary heart disease physicians
    """ 
    # parsed html by using lxml
    # In the following processing
    # the one ending in org is the raw data in the HTML
    # the one ending in inf is the processed data by extracting from raw data
    select = etree.HTML(html)
    
    name_org = select.xpath('//div[@class="oh zoom lh180"]//a[@class="blue_a3"]//text()')
    name_inf = [i.strip() for i in name_org if len(i.strip()) > 0]
    
    hospital_org = select.xpath('//div[@class="oh zoom lh180"]//span[@class="ml10"]//text()')
    hospital_inf = [i.strip() for i in hospital_org if len(i.strip()) > 0]
    
    hot_org = select.xpath('//div[@class="oh zoom lh180"]//span[@class="patient_recommend"]//i[@class="blue"]//text()')
    hot_inf = [i.strip() for i in hot_org if len(i.strip()) > 0]
    
    ticket_within2_inf = [] 
    ticket_sum_inf = []
    ticket_org = select.xpath('//div[@class="oh zoom lh180"]//span//text()')
    ticket_inf = [i.strip().split('/') for i in ticket_org if len(i.strip()) > 0 and i[0:6] == '2年内该疾病']
    for i in range(len(ticket_inf)):
        ticket_within2_inf.append(ticket_inf[i][0][8:])
        ticket_sum_inf.append(ticket_inf[i][1][5:])
    
    answer_inf = select.xpath('//span[@class="patient_recommend_ora"]//text()')
    org = select.xpath('//div[@class="oh zoom lh180"]//text()')
    inf = [i.strip() for i in org if len(i.strip()) > 0]
    index_1 = [i for i in range(len(inf)) if inf[i][0:6] == '2年内该疾病']
    index_2 = [i for i in range(len(inf)) if inf[i][0:6] == '近两周回复']
    for i in range(len(index_1)):
        if len(index_2) == i:
            break
        if index_1[i] != index_2[i] - 1:
            index_2.insert(i, index_1[i] + 1)
            answer_inf.insert(i, 0)
    while i < len(index_1):
        index_2.append(index_1[i] + 1)
        answer_inf.append(0)
        i += 1
    
    data = []
    for i in range(len(name_inf)):
        dic = {}
        dic['姓名'] = name_inf[i]
        dic['医院'] = hospital_inf[i]
        dic['推荐热度'] = hot_inf[i]
        dic['两年内该疾病得票'] = ticket_within2_inf[i]
        dic['该疾病总票'] = ticket_sum_inf[i]
        dic['近两周回复'] = answer_inf[i]
        data.append(dic)
    
    return data
        
    
def main(page, header, save_path):
    """
    Input: a page number to product a url
    """
    url_head = 'https://www.haodf.com/jibing/guanxinbing/daifu_all_all_all_all_all_all_'
    url = url_head + str(page) + '.htm'
    html = get_page_html(url)
    data = get_doctor_info(html)
    save_data(data, header, save_path)
    

if __name__ == '__main__':
    ##########  input parameter  ##########
    date = '19700101' # 专属测试日期
    
    
    # set store file structure
    save_path = 'C:/Users/lenovo/Desktop/HDF_data/02_data/1_冠心病主界面数据/'+ date + '_doctor_summary_page.csv'
    header = ['姓名', '医院', '推荐热度', '两年内该疾病得票', '该疾病总票','近两周回复']
    save_data_header(header, save_path)
    
    for page in range(1,68):
        main(page, header, save_path)
        # process bar
        print(page)
