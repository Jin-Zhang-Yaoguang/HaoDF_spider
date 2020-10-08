# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 23:53:02 2020

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
            url_dic[row['姓名']] = row['患者问诊链接']
    
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
        return datetime.date(int(process_string[:4]), int(process_string[5:7]),int(process_string[8:]))
    
    
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
        response = requests.get(url=url,headers=headers)
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


def get_detail_consult_info(html,doctor_name,spider_date):
    consult_detail_info = {} 
    select = etree.HTML(html)
    
    try:
        title_org = select.xpath('//div[@class="fl-title ellps"]//text()')
        title_inf = [i.strip() for i in title_org if len(i.strip()) > 0][0]
    except:
        title_inf = '未填写'
    try:    
        status_org = select.xpath('//div[@class="f-c-l-status"]//span[@class="f-c-l-s-green"]//text()')
        status_inf = [i.strip().replace('(','') for i in status_org if len(i.strip()) > 0][0]
    except:
        status_inf = '未填写'
    try:
        type_org = select.xpath('//h2[@class="f-c-r-w-title"]//text()')
        type_inf = [i.strip() for i in type_org if len(i.strip()) > 0][0]
    except:
        type_inf =  '未填写'
    try:
        date_org = select.xpath('//div[@class="f-c-r-date-right"]//text()')
        date_inf = [i.strip() for i in date_org if len(i.strip()) > 0][0]
    except:
        date_inf = '未填写'
    info_type = ['疾病','病情描述', '希望获得的帮助','患病多久','已就诊医院及科室','用药情况','既往病史']
    info_org = select.xpath('//div[1][@class="f-card clearfix js-f-card"]//div[@class="f-c-r-wrap"]//text()')
    info_inf = [i.strip() for i in info_org if len(i.strip()) > 0]
    
    q_and_a_summary = {}
    record = 2
    q_and_a_org = select.xpath('//div['+str(record)+'][@class="f-card clearfix js-f-card"]//text()')
    q_and_a_inf = [i.strip() for i in q_and_a_org if len(i.strip()) > 0]
    while len(q_and_a_inf) != 0:
        try:
            q_and_a_detail = {}
            q_and_a_detail['对话序号'] = record
            if q_and_a_inf[5][:4] == '郑重提示' or q_and_a_inf[0] == doctor_name:
                q_and_a_detail['对话发起人'] = '医生'
                q_and_a_detail['对话时间'] = process_date(spider_date, q_and_a_inf[2])
                q_and_a_detail['对话内容'] = q_and_a_inf[4]
            else:
                q_and_a_detail['对话发起人'] = '患者'
                q_and_a_detail['对话时间'] = process_date(spider_date, q_and_a_inf[3])
                q_and_a_detail['对话内容'] = q_and_a_inf[5]
            q_and_a_summary['序号'+str(record)] = q_and_a_detail
        except:
            pass
        record += 1
        q_and_a_org = select.xpath('//div['+str(record)+'][@class="f-card clearfix js-f-card"]//text()')
        q_and_a_inf = [i.strip() for i in q_and_a_org if len(i.strip()) > 0]
    
    consult_detail_info['标题'] = title_inf
    consult_detail_info['问诊类型'] = type_inf
    consult_detail_info['提问状态'] = status_inf
    consult_detail_info['提问日期'] = date_inf
    for i in range(len(info_inf)):
        if info_inf[i] in info_type:
            consult_detail_info[info_inf[i]] = info_inf[i+1]
    consult_detail_info['问诊明细汇总'] = q_and_a_summary
    return consult_detail_info


def get_summary_consult_info(html,doctor_name,doctor_consult_url,spider_date):
    doctor_info_summary = []
    select = etree.HTML(html)
    ago7_date = spider_date + datetime.timedelta(days=-6)
    
    name_org = select.xpath('//div[@class="zixun_list"]//text()')
    name_inf = [i.strip().replace('(','') for i in name_org if len(i.strip()) > 0 and i.strip() not in [')','by']][5:215]
    link_org = select.xpath('//div[@class="zixun_list"]//a[@class="td_link"]//@href')

    for i in range(len(link_org)):
        doctor_info = {}
        doctor_info['医生姓名'] = doctor_name
        doctor_info['患者问诊链接'] = doctor_consult_url
        doctor_info['患者'] = name_inf[7*i]
        doctor_info['相关疾病'] = name_inf[7*i + 2]
        doctor_info['对话数'] = name_inf[7*i + 3]
        doctor_info['医生回复数'] = name_inf[7*i + 4]
        doctor_info['最后发表时间'] = datetime.date(int(name_inf[7*i + 5][:4]), int(name_inf[7*i + 5][5:7]),int(name_inf[7*i + 5][8:]))
        doctor_info['最后发表人'] = '患者' if name_inf[7*i + 6] == name_inf[7*i] else '医生'
        doctor_info['明细链接'] = link_org[i]
        doctor_info['时间是否有效'] = 1 if doctor_info['最后发表时间'] >= ago7_date else 0
        
        if doctor_info['时间是否有效'] == 1:
            html_detail = get_doctor_html(link_org[i])
            doctor_detail_info = get_detail_consult_info(html_detail,doctor_name,spider_date)
            doctor_info = {**doctor_info, **doctor_detail_info} 
        doctor_info_summary.append(doctor_info)
    
    next_page_flag = doctor_info['时间是否有效']
    return next_page_flag, doctor_info_summary


def main(doctor_name, doctor_consult_url, save_path, header, spider_date):
    now_page, next_page_flag = 1, 1
    while next_page_flag == 1:
        spider_url = doctor_consult_url + '?p_type=all&p=' + str(now_page)
        html = get_doctor_html(spider_url)
        next_page_flag, doctor_info_summary = get_summary_consult_info(html, doctor_name, doctor_consult_url, spider_date)
        save_data(doctor_info_summary, header, save_path)
        now_page += 1
        
        
if __name__ == '__main__':
    ##########  input parameter  ##########
    date = '20201008' 
    spider_date = datetime.date(int(date[:4]), int(date[4:6]),int(date[6:]))
    
    
    # read csv: get all doctor personal website
    file_path = r'C:\Users\lenovo\Desktop\HDF_data\02_data\0_静态数据\doctor_static_info.csv'
    consult_url_dic = read_data(file_path)

    # set store file structure
    save_path = 'C:/Users/lenovo/Desktop/HDF_data/02_data/5_患者问诊数据/'+ date + '_doctor_consult.csv'
    header = ['医生姓名', '患者问诊链接', '爬取问诊链接', 
              '患者', '标题', '相关疾病', '对话数', '医生回复数', 
              '最后发表时间', '最后发表人', '明细链接',
              '问诊类型', '提问状态', '提问日期', '疾病', '病情描述',
              '希望获得的帮助', '患病多久', '已就诊医院及科室',
              '用药情况', '既往病史', '问诊明细汇总', '时间是否有效']
    
    save_data_header(header, save_path)

    count = 0
    for doctor_name, doctor_consult_url in consult_url_dic.items():
        count += 1
        main(doctor_name, doctor_consult_url, save_path, header, spider_date)
        
        # processing bar
        print(count)
