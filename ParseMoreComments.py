
# coding: utf-8

# In[ ]:


import requests
from datetime import datetime
import time
#from tqdm import tqdm
from tqdm import tqdm_notebook as tqdm
from random import random
import pandas
import winreg
import xlrd

def get_desktop():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,                          r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',)
    return winreg.QueryValueEx(key, "Desktop")[0]

class MaoYan():
    """docstring for ClassName"""
    def __init__(self, movie_id):
        #print('*******MaoYan_spider******')
        self.movie_id = movie_id
        #self.starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.starttime = int(round(time.time() * 1000))
        #self.starturl = 'http://m.maoyan.com/mmdb/comments/movie/%s.json?_v_=yes&offset=0&startTime=%s'%(movie_id,self.starttime)
        self.starturl = 'http://m.maoyan.com/review/v2/comments.json?movieId=%s&userId=-1&offset=0&limit=15&ts=%s&level=2&type=3' %(movie_id,self.starttime)
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
        
    def GetCommentNum(self):
        '''
        查询总评论数
        用于建立循环
        '''
        response = requests.get(self.starturl,headers = self.headers)
        text = response.json()
        num = text['data']['t2total']
        showtime = pandas.to_datetime(self.starttime,unit='ms')
        print('>>>>查询时间：%s\n>>>>评论数量：%s' %(showtime,num))
        return num

    def FormatUrl(self,starttime):
        #url = 'http://m.maoyan.com/mmdb/comments/movie/%s.json?_v_=yes&offset=15&startTime=%s'%(self.movie_id,starttime)
        url = 'http://m.maoyan.com/review/v2/comments.json?movieId=%s&userId=-1&offset=0&limit=15&ts=%s&level=2&type=3' %(self.movie_id,starttime)
        return url

    def QueryComent(self,url):
        '''
        评论请求部分
        nickName:用户昵称
        cityName:城市
        content:评论内容
        score:用户评分
        startTime:评论时间，每次取最早的时间传入下次请求
        '''
        time.sleep(random())
        try:    
            response = requests.get(url, headers = self.headers, timeout = 5)
            if response.status_code == 200:
                attrs = ''
                comments = response.json()['data']['comments']
                for index in range(0,len(comments)):
                    try:
                        c_id = comments[index]['id']
                        m_id = comments[index]['movieId']
                        u_id = comments[index]['userId']
                        nickName = comments[index]['nick']
                        content = comments[index]['content'].replace('\n', ' ', 10).replace('\r', ' ', 10) if 'content' in comments[index] else ''
                        score = comments[index]['score']
                        startTime = comments[index]['startTime']
                        startTime1 = pandas.to_datetime(startTime,unit='ms')
                        param = '|%s|%s|%s|%s|%s|%s|%s\n'%(m_id,c_id,startTime1,u_id,nickName,score,content)
                        attrs = attrs+param
                    except KeyError as e:
                        attrs = ''      
                return attrs ,startTime, True
            else:
                print('>>>>查询过于频繁，请休息几分钟️️')
                return response.content.encode('utf-8'),'',False
        except BaseException as e:
            print('>>>>请检查网络...')
            #print(e)
            #print(response.content.decode('utf-8'))
            return e,'',False

    def SaveComent(self,movie_id):
        '''
        保存评论到txt文件
        如果请求成功保存，失败sleep100秒
        tqdm用于实现进度条
        '''
        num = self.GetCommentNum()
        pages = int(num/15)
        file_name =  r"%s\comments\more_comment%s.txt" %(get_desktop(),movie_id)
        with open(file_name,'wb')  as f: 
            for i in tqdm(range(0,pages+1)):
                if i == 0:
                    starttime = self.starttime
                    url = self.FormatUrl(starttime)
                    attrs,starttime,IsOk = self.QueryComent(url)
                else:
                    url = self.FormatUrl(starttime)
                    attrs,starttime,IsOk = self.QueryComent(url)
                if IsOk:
                    f.write(attrs.encode('utf-8'))
                else:
                    for i in range(3):
                        time.sleep(3)
                        attrs,starttime,IsOk = self.QueryComent(url)
                        if IsOk:
                            f.write(attrs.encode('utf-8'))
                            break
                        else:
                            continue
            print ('>>>>评论保存完毕...')

def get_result(movie_id):
    p = MaoYan(movie_id)
    p.SaveComent(movie_id)
    return 1

MovieListPath = r"%s\movie_list.xlsx" %(get_desktop())
workbook = xlrd.open_workbook(MovieListPath)
first_sheet = workbook.sheet_by_index(0)
movie_list = first_sheet.col_values(0) #倒时候改这个,0,1,2,3
while '' in movie_list:
    movie_list.remove('')
print(len(movie_list))
for m in tqdm(range(1,len(movie_list))):
    print('movie_id:',int(movie_list[m]))
    get_result(int(movie_list[m]))

