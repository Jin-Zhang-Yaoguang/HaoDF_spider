# HaoDF_spider
## 1. Background
本项目获取好大夫在线（www.haodf.com ）中的相关信息，仅供学习交流使用，如果侵权联系删除。  
This project obtains the relevant information in Haodf (www.haodf.com), only for learning and communication. If the infringement contact is deleted.
## 2. Introduction
名称|命名|爬取字段|示例链接
:---|:--|:------|:--------
爬取冠心病主界面|	doctor_summary_page.py|姓名<br/>推荐热度<br/>两年内该疾病的票<br/>该疾病总票<br/>近两周回复|	https://www.haodf.com/jibing/guanxinbing/daifu_all_all_all_all_all_all_1.htm
爬取医生个人界面 | 姓名<br/>个人网站链接 【主键/外键】<br/>基础信息：职称，医院，科室，性别<br/>标题栏数据：3个<br/>侧边栏数据：12个<br/>主题栏数据：疗效满意度、态度满意度、几届好大夫、具体届数、简历|	https://fwliuhaibo.haodf.com/| doctor_personal_info.py
爬取服务价格链接|	doctor_service_price.py |姓名<br/>在线问诊链接<br/>一问一答<br/>图文问诊<br/>电话问诊|	https://fwliuhaibo.haodf.com//clinic/selectclinicservice
爬取患者投票链接| doctor_voted.py |	医生姓名<br/>医生投票链接 【主键/外键】<br/>爬取界面链接<br/>投票类型<br/>患者姓名<br/>病症类型<br/>看病目的<br/>治疗方式<br/>疗效满意度<br/>态度满意度<br/>门诊花费<br/>目前病情状态<br/>本次挂号途径<br/>选择该医生的理由<br/>评论内容<br/>推荐人数<br/>回应人数<br/>投票时间<br/>时间是否有效|	https://www.haodf.com/jingyan/all-liuhaibo.htm
爬取患者问诊链接|	doctor_consulted.py |医生姓名<br/>患者问诊链接  【主键/外键】<br/>爬取问诊链接<br/>患者<br/>标题<br/>相关疾病<br/>对话数<br/>医生回复数<br/>最后发表时间<br/>最后发表<br/>明细链接<br/>问诊类型<br/>提问状态<br/>提问日期<br/>疾病<br/>病情描述<br/>希望获得的帮助<br/>患病多久<br/>已就诊医院及科室<br/>用药情况<br/>既往病史<br/>问诊明细汇总<br/>每个单元含：对话序号、对话发起人、对话时间、对话内容|	https://fwliuhaibo.haodf.com//zixun/list.htm
爬取心意礼物链接|	doctor_gift_detail.py |	医生姓名<br/>心意礼物链接 【主键/外键】<br/>已帮助患者数<br/>已收到礼物数<br/>收到礼物明细  json数据结构|	https://fwliuhaibo.haodf.com/present/presentnavigation
爬取患友会链接|	doctor_patient_group.py |	医生姓名<br/>患友会链接 【主键/外键】<br/>患友会数量<br/>患友会详情（每个患友会的名称、成员数、话题数）|	https://fwliuhaibo.haodf.com/huanyouhui/index.html
