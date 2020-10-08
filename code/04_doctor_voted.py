# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 09:31:41 2020

@author: Jin Zhang
"""

import requests
import time
import csv
import datetime
from lxml import etree


def read_data(file_path):
    url_dic = {}
    with open(file_path,'r',encoding='utf-8-sig') as myFile:  
        reader = csv.DictReader(myFile)
        for row in reader:
            url_dic[row['姓名']] = row['患者投票链接']
    
    return url_dic


def save_data_header(header, save_path):
    with open(save_path, 'a', newline='',encoding='utf-8-sig') as f: 
        writer = csv.DictWriter(f,fieldnames=header) 
        writer.writeheader()
    
    
def save_data(doctor_data, header, save_path):
    data = doctor_data
    with open(save_path, 'a', newline='',encoding='utf-8-sig') as f: 
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writerows(data) 


def process_date(spider_date, process_string):
    if '今天' in process_string:
        return spider_date
    elif '昨天' in process_string:
        return spider_date + datetime.timedelta(days=-1)
    elif len(process_string) < 8:
        return datetime.date(spider_date.year, int(process_string[:2]),int(process_string[3:]))
    else:
        return datetime.date(int(process_string[:4]), int(process_string[5:7]),int(process_date[8:]))
    

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


def get_doctor_info(name, vote_url, spider_url, html, spider_date):    
    # create a dictionary to save data
    doctor_info = {}
    
    # parsed html by using lxml
    # In the following processing
    # the one ending in org is the raw data in the HTML
    # the one ending in inf is the processed data by extracting from raw data
    select = etree.HTML(html)
    
    # part1: basic infomation
    
        
    # part2: list information
    name_org = select.xpath('//div[@class="patient-eva-header"]//span[@class="patient-name"]//text()')
    name_inf = [i.strip().replace('患者：','') for i in name_org if len(i.strip()) > 0]
    illness_org = select.xpath('//div[@class="patient-eva-header"]//span[@class="disease-tag"]//text()')
    illness_inf = [i.strip() for i in illness_org if len(i.strip()) > 0]
    comment_org = select.xpath('//div[@class="eva-detail"]//text()')
    comment_inf = [i.strip() for i in comment_org if len(i.strip()) > 0]
    describe_org = select.xpath('//div[@class="clearfix"]//span[@class="patient-sumary-item"]//text()')
    describe_inf = [i.strip().split('：') for i in describe_org if len(i.strip()) > 0 and i.strip()[:6] != '本次挂号途径']
    describe_inf.append(['看病目的','用来终结判断'])
    
    doctor_info_summary = []
    for i in range(len(name_inf)):
        doctor_info = {}
        doctor_info['医生姓名'] = name
        doctor_info['医生投票链接'] = vote_url
        doctor_info['爬取界面链接'] = spider_url
        doctor_info_summary.append(doctor_info)
        
    vote_row = 0
    describe_row = 0
    while vote_row < len(name_inf):
        doctor_info = doctor_info_summary[vote_row]
        doctor_info['患者姓名'] = name_inf[vote_row]
        doctor_info['病症类型'] = illness_inf[vote_row]
        doctor_info['投票类型'] = comment_inf[vote_row][:4] if comment_inf[vote_row][:4] == '看病经验' else comment_inf[vote_row][:3]
        doctor_info['评论内容'] = comment_inf[vote_row]
        flag = 1
        while flag:
            doctor_info[describe_inf[describe_row][0]] = describe_inf[describe_row][1]
            describe_row += 1
            flag = 0 if describe_inf[describe_row][0] == '看病目的' else 1
        vote_row += 1
    
    # part3: date infomation
    date = spider_date
    date = datetime.date(int(date[:4]), int(date[4:6]),int(date[6:]))
    ystd_date = date + datetime.timedelta(days=-1)
    ago7_date = date + datetime.timedelta(days=-6)
    date_org = select.xpath('//div[@class="eva-footer clearfix"]//text()')
    date_inf = [i.strip() for i in date_org if len(i.strip()) > 0 and i.strip() not in ['这条有参考价值吗？','有','|', '回应',]]
    for i in range(len(date_inf)):
        if date_inf[i][-1] != ')':
            if date_inf[i][:2] == '昨天':
                date_inf[i] = ystd_date
            else:
                date_inf[i] = datetime.date(int(date_inf[i][:4]), int(date_inf[i][5:7]),int(date_inf[i][8:]))
    
    date_inf.append(0)

    vote_row = 0
    describe_row = 0
    while vote_row < len(name_inf):
        doctor_info = doctor_info_summary[vote_row]
        doctor_info['投票时间'] = date_inf[describe_row].strftime("%Y-%m-%d")
        doctor_info['时间是否有效'] = 1 if date_inf[describe_row] >= ago7_date else 0
        describe_row += 1
        while type(date_inf[describe_row])is str:
            if date_inf[describe_row][-3:-1] == '推荐':
                doctor_info['推荐人数'] = date_inf[describe_row][1:-4]
            elif date_inf[describe_row][-3:-1] == '回应':
                doctor_info['回应人数'] = date_inf[describe_row][1:-4]
            describe_row += 1
        vote_row += 1
    
    # part4: cal next_page_flag
    next_page_flag = 0
    for i in doctor_info_summary:
        if i['时间是否有效'] == 1:
            next_page_flag = 1
            break
        
    return next_page_flag, doctor_info_summary
    
    
def main(name, vote_url, save_path, header, spider_date):
    now_page = 1
    next_page_flag = 1
    spider_url_head = vote_url[:-4]
    while next_page_flag:
        spider_url = spider_url_head + '/' + str(now_page) + '.htm'
        html = get_doctor_html(spider_url)
        next_page_flag, doctor_info_summary = get_doctor_info(name, vote_url, spider_url, html, spider_date)  
        save_data(doctor_info_summary, header, save_path)
        now_page += 1


if __name__ == '__main__':
    ##########  input parameter  ##########
    date = '20201004' 
    
    
    # read csv: get all doctor personal website
    file_path = r'C:\Users\lenovo\Desktop\HDF_data\02_data\0_静态数据\doctor_static_info.csv'
    vote_url_dic = read_data(file_path)

    # set store file structure
    save_path = 'C:/Users/lenovo/Desktop/HDF_data/02_data/4_患者投票数据/'+ date + '_doctor_voted.csv'
    header = ['医生姓名', '医生投票链接', '爬取界面链接', '投票类型','患者姓名','病症类型',
              '看病目的','治疗方式','疗效满意度','态度满意度','门诊花费',
              '目前病情状态','本次挂号途径','选择该医生的理由',
              '评论内容','推荐人数','回应人数','投票时间','时间是否有效']

    save_data_header(header, save_path)
    
    count = 0
    for doctor_name, doctor_vote_url in vote_url_dic.items():
        count += 1
        print(doctor_name, doctor_vote_url)
        main(doctor_name, doctor_vote_url, save_path, header, date)
        
        # processing bar
        if count % 10 == 0:
            print(count)
