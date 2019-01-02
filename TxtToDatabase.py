
# coding: utf-8

# In[ ]:


# -*- coding: UTF-8 -*-
import pymysql as mdb
import time
#from tqdm import tqdm
from tqdm import tqdm_notebook as tqdm
import os 
g = os.walk(r"C:\Users\fmche\Desktop\comments")  
list_file=[]
for path,dir_list,file_list in g:  
    for file_name in file_list:  
        list_file.append(os.path.join(file_name))
        
start=time.time()
def save_to_mysql(filename):
    #将con设定为全局连接
    db = mdb.connect(host='localhost',user='root',password='*****',port=3306, db='maoyan')
    cursor = db.cursor()
#   filename = 'selected_comment342578.txt'
    file_object = open(filename,'rb')
    desc1 = 'inserting_%s' %(list_file[i])
    for line in tqdm(file_object,desc = desc1): 
        line_list = str(line, 'utf-8')
        line_list = line_list.split('|')
        if len(line_list) == 8: 
            sql = "INSERT INTO comments(m_id, c_id, c_date, u_id, u_name, u_rate, c_content)                    VALUES(%s,%s,%s,%s,%s,%s,%s)"
            par = (line_list[1], line_list[2], line_list[3],line_list[4],line_list[5],line_list[6],line_list[7])
            try:
                cursor.execute(sql,par)
                db.commit()
            except:
                db.rollback()
    db.close()
    file_object.close()
    return 1

for i in tqdm(range(len(list_file)),desc='comments file'):
    filename = r"C:\Users\fmche\Desktop\comments\%s" %(list_file[i])    
    save_to_mysql(filename)
print(time.time()-start)
print('done')


# In[ ]:


import pymysql as mdb

db = mdb.connect(host='localhost',user='root',password='*****',port=3306, db='maoyan')
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS comments")
create_sql = 'CREATE TABLE IF NOT EXISTS comments(    m_id int(64) NOT NULL,    c_id int NOT NULL,    c_date datetime NOT NULL,    u_id int NOT NULL,    u_name varchar(30) NOT NULL,    u_rate int NOT NULL,    c_content varchar(350) NOT NULL,    PRIMARY KEY (c_id))'
cursor.execute(create_sql)
db.close()

