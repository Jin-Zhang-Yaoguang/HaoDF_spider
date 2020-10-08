# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 13:22:21 2020

@author: Jin Zhang
"""

import requests
import time
import csv
from lxml import etree


def read_data(file_path):
    url_list = []
    with open(file_path,'r',encoding='utf-8-sig') as myFile:  
        reader = csv.DictReader(myFile)
        for row in reader:
            url_list.append(row['心意礼物链接'])
    
    return url_list


def save_data_header(header, save_path):
    with open(save_path, 'a', newline='',encoding='utf-8-sig') as f: 
        writer = csv.DictWriter(f,fieldnames=header) 
        writer.writeheader()
    
    
def save_data(doctor_data, header, save_path):
    data = [doctor_data]
    with open(save_path, 'a', newline='',encoding='utf-8-sig') as f: 
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writerows(data) 


def get_doctor_html(url):
    """
    Input: a url of the doctor's service price website
    
    Output: unparsed html
    """
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cookie':'UM_distinctid=1723c69e66978f-013966aacf6d08-d373666-e1000-1723c69e66a598; _ga=GA1.2.1165242677.1590151473; g=HDF.155.5ec7c93981199; __jsluid_s=88f2e39ecd2f900df725f2e3fd516692; CNZZDATA-FE=CNZZDATA-FE; newaskindex=1; _gid=GA1.2.1915212418.1601454891; Hm_lvt_dfa5478034171cc641b1639b2a5b717d=1601348462,1601348501,1601454891,1601458813; PHPSESSID=36080cee57d351f5454088249dc392eb; Hm_lpvt_dfa5478034171cc641b1639b2a5b717d=1601474418',
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
        response.encoding = 'cp936'

        html = response.text
        status_code = response.status_code
        print(status_code)
        
        count += 1
        time.sleep(count*0.1)
    
    #print(html)
    #print(count)
    #print(response.status_code)
    return html


def get_doctor_info(url, html):    
    # create a dictionary to save data
    doctor_info = {}
    
    # parsed html by using lxml
    # In the following processing
    # the one ending in org is the raw data in the HTML
    # the one ending in inf is the processed data by extracting from raw data
    select = etree.HTML(html)
    
    name_org = select.xpath('//div[@class="profile-text"]//h1[@class="doctor-name"]//text()')
    name_inf = [i.strip() for i in name_org if len(i.strip()) > 0]
    
    gift_org = select.xpath('//p[@class="gift_top_con"]//span[@class="fl pt10"]//strong[@class="orange1 fy pl5 pr5"]//text()')
    gift_inf = [i.strip() for i in gift_org if len(i.strip()) > 0]
    
    gift_detail = {}
    gift_detail_org = select.xpath('//p[@class="gift_name"]//text()')
    gift_detail_inf = [i.strip() for i in gift_detail_org if len(i.strip()) > 0 and i != ')']
    
    for i in range(len(gift_detail_inf)//2):
        gift_detail[gift_detail_inf[2*i][:-1]] = gift_detail_inf[2*i+1]
    
    doctor_info['姓名'] = name_inf[0]
    doctor_info['心意礼物链接'] = url
    doctor_info['已帮助患者数'] = gift_inf[0]
    doctor_info['已收到礼物数'] = gift_inf[1]
    doctor_info['收到礼物明细'] = gift_detail
    
    return doctor_info
    
    
def main(url, save_path, header):
    html = get_doctor_html(url)
    doctor_info = get_doctor_info(url,html)  
    save_data(doctor_info, header, save_path)

    

if __name__ == '__main__':
    ##########  input parameter  ##########
    date = '19700101' 

    
    # read csv: get all doctor personal website
    file_path = r'C:\Users\lenovo\Desktop\HDF_data\02_data\0_静态数据\doctor_static_info.csv'
    doctor_gift_url_list = read_data(file_path)

    # set store file structure
    save_path = 'C:/Users/lenovo/Desktop/HDF_data/02_data/6_心意礼物数据/'+ date + '_doctor_detail_gift.csv'
    header = ['姓名', '心意礼物链接', '已帮助患者数', '已收到礼物数', '收到礼物明细']
    save_data_header(header, save_path)
    
    # get doctor info
    count = 0
    for url in doctor_gift_url_list[:40]:
        count += 1
        main(url, save_path, header)
        # processing bar
        if count % 10 == 0:
            print(count)
