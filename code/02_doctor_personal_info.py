# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 16:17:33 2020

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
            url_list.append(row['医生个人链接'])
    
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
    Input
    ------
    a url of the doctor's personal website
    e.g. https://fwliuhaibo.haodf.com/
    
    Output
    ------
    html: unparsed html
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
    """
    Input
    ------
    the unparsed html of the doctor
    
    Output
    ------
    doctor infomation: the data of the doctor's personal website
    You can refer to a data dictionary for specific fields
    """
    
    # create a dictionary to save data
    doctor_info = {}
    
    # parsed html by using lxml
    # In the following processing
    # the one ending in org is the raw data in the HTML
    # the one ending in inf is the processed data by extracting from raw data
    select = etree.HTML(html)
    
    # part 1: get basic information about your doctor
    # attribute: Name, Title, Hospital, Department
    name_org = select.xpath('//div[@class="profile-text"]//h1[@class="doctor-name"]//text()')
    name_inf = name_org[0].strip()
    
    title_org = select.xpath('//div[@class="profile-text"]//span[@class="positon"]//text()')
    title_inf = [i.strip() for i in title_org if len(i.strip()) > 0]
    title_inf = ' '.join(title_inf)
    
    hospital_department_org = select.xpath('//div[@class="profile-text"]//p[@class="doctor-faculty"]//text()')
    hospital_department_inf = [i.strip() for i in hospital_department_org if len(i.strip()) > 0]
    hospital_inf = hospital_department_inf[0]
    department_inf = hospital_department_inf[1]
    
    doctor_info['姓名'] = name_inf
    doctor_info['职称'] = title_inf
    doctor_info['医院'] = hospital_inf
    doctor_info['科室'] = department_inf
    
    # part2: get header format data
    org = select.xpath('//div[@class="profile-sta"]//text()')
    inf = [i.strip() for i in org if len(i.strip()) > 0 and i.strip() != '%']
    for i in range(len(inf)//2):
        doctor_info[inf[2*i]] = inf[2*i + 1]
      
    
    # part3: get sidebar format data
    org_1 = select.xpath('//div[@class="item-body"]//div[@class="clearfix"]//div[@class="per-sta-label"]//text()')
    org_2 = select.xpath('//div[@class="item-body"]//div[@class="clearfix"]//div[@class="per-sta-data"]//text()')
    for i in range(len(org_1)):
        doctor_info[org_1[i][:-1]] = org_2[i]
    
    # part4: get body format data
    honour_org = select.xpath('//div[@class="honour-header"]//text()')
    honour_inf = ''.join([i.strip() for i in honour_org])
    
    honour_detail_org = select.xpath('//li[@class="honour-title"]//text()')
    honour_detail_inf = [i.strip()[:4] for i in honour_detail_org if len(i.strip()) > 0]
    honour_detail_inf = ' '.join(honour_detail_inf)
    
    satisfaction_org = select.xpath('//div[@class="item-body"]//div[@class="satisfaction clearfix"]//i[@class="sta-num"]//text()')
    satisfaction_inf = [i.strip() for i in satisfaction_org if len(i.strip()) > 0 and i.strip() != '%']
    
    resume_org = select.xpath('//div[@class="good-at-text"]//text()')
    resume_inf = [i.strip() for i in resume_org]
    if len(resume_inf) <= 20:
        resume_inf = ''.join(resume_inf)
    resume_inf = ''.join(resume_inf[:20])
    
    star_org = select.xpath('//div[@class="experience-row clearfix"]//span[@class="experience-label"]//text()')
    star_inf = 1 if len(star_org) >= 1 else 0

    doctor_info['好大夫届数'] = honour_inf
    doctor_info['好大夫具体年份'] = honour_detail_inf
    doctor_info['简历'] = resume_inf 
    doctor_info['诊后服务星'] = star_inf
    try:
        doctor_info['疗效满意度'] = satisfaction_inf[0]
        doctor_info['态度满意度'] = satisfaction_inf[1]
    except:
        pass
    
    # part5: personal url
    personal_url = url
    doctor_info['医生个人链接'] = personal_url
    
    return doctor_info
    

def main(url, save_path, header):
    """
    Input
    ------
    a doctor personal website url
    
    Process
    ------
    Get the data from the URL and store it in a file
    """
    html = get_doctor_html(url)
    doctor_info = get_doctor_info(url,html)  
    save_data(doctor_info, header, save_path)

    

if __name__ == '__main__':
    ##########  input parameter  ##########
    date = '19700101' 

    
    # read csv: get all doctor personal website
    file_path = r'C:\Users\lenovo\Desktop\HDF_data\02_data\0_静态数据\doctor_static_info.csv'
    doctor_url_list = read_data(file_path)

    # set store file structure
    save_path = 'C:/Users/lenovo/Desktop/HDF_data/02_data/2_医生个人界面数据/'+ date + '_doctor_personal_info.csv'
    header = ['姓名', '职称', '医院', '科室', '性别', '工作城市', '是否三甲',
              '综合推荐热度', '在线服务满意度', '在线问诊量', 
              '总访问', '昨日访问', '总文章', '总患者', '昨日诊后报到患者', 
              '微信诊后报到患者', '总诊后报到患者', '患者投票', '感谢信', 
              '心意礼物', '上次在线', '开通时间', 
              '好大夫届数', '好大夫具体年份', '疗效满意度', '态度满意度', '简历', '诊后服务星',
              '医生个人链接']
    save_data_header(header, save_path)

    # get doctor info
    count = 0
    for url in doctor_url_list:
        count += 1
        main(url, save_path, header)
        # processing bar
        if count % 10 == 0:
            print(count)
