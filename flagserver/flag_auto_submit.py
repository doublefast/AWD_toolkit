#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: 36huo
# ------------------------------------------------
# read http request from txt file
# replace 

import socket
import time
import random
import re
import subprocess
import sqlite3
import time
import sys
import getopt


class flag_auto_submit_class(object):
    def __init__(self,db_file,protocol,flag_submit_request_file,sleep_time):
        self.db_file=db_file
        self.protoco = protocol
        self.flag_submit_request_file = flag_submit_request_file
        self.sleep_time = sleep_time
        self.con = sqlite3.connect(db_file)
        self.con.row_factory = self.dict_factory

    @classmethod
    # 将查询结果转为字典，方便使用
    # 自定义row构造器，返回字典对象，可以通过列名索引
    def dict_factory(self,cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def getflags(self):
        c = self.con.cursor()
        cursor = c.execute("select id,ip,flag from flag_submit where submitted=0")
        rows = cursor.fetchall()
        return rows

    def creat_payload(self,payload_file,flag,ip):
        with open(payload_file,'r') as f:
            payload=f.read()

        payload=payload.replace('\r','').replace('{flag}',flag).replace('{ip}',ip)
        # 分离 header 和 http body部分
        headers_text, body = payload.split('\n\n',2)
        # 分离header
        http_headers=headers_text.split('\n')

        # 手动更新Content-Length:  弃用
        # payload=re.sub(r'Content-Length: \d+','Content-Length: '+str(len(body)),payload)

        # 正则获取 Host中的 ip/域名 和端口号
        match=re.search(r'Host: (.*?)(:.*?)?\n',payload)
        if match.group(2) is None:
            PORT=80
        else:
            PORT=int(match.group(2)[1:])
        Host_name=match.group(1)

        # 通过header 首行获取 相关信息
        http_method,http_uri,http_version=http_headers[0].split(' ')
        #print(http_method,match.group(1)+':'+str(PORT)+http_uri,body)

        #开始拼接wget命令
        wget_command='wget -O- -q -T 2 -t 2 --no-check-certificat '
        for header in  http_headers[1:]:
            if header[0:15]!='Content-Length:':
                wget_command+='--header="%s" ' % header

        # 如果没有post内容，不设置--post-data参数
        if body.strip()!="":
            wget_command+='--post-data "%s" ' % body.strip()

        # 默认http协议
        wget_command+="http://%s:%s%s" % (Host_name,PORT,http_uri)
        return wget_command


    def run(self):
        #去数据库读取 尚未提交的flag
        flags=self.getflags()
        for flag in flags:
            # print(flag,flag['flag'])

            # 生成wget命令，并执行
            output=''
            try:
                output=subprocess.check_output(self.creat_payload(self.flag_submit_request_file,flag['flag'],flag['ip']),shell=True)
            except:
                continue

            print(flag['id'],flag['ip'],flag['flag'],output)

            # 如果wget命令执行成功，则将数据库里该条记录设置为已提交
            param=[1,int(time.time()),output,flag['id']]
            self.con.execute("UPDATE flag_submit set submitted=?,submit_time=?,comments=? where id=?",param)
            self.con.commit()
            time.sleep(self.sleep_time)

def main(argv):
    protocol='http'
    sleep_time=3
    db_file='db.db'
    flag_submit_request_file='flag_submit_request.txt'
    try:
        opts, args = getopt.getopt(argv,"hr:d:p:t:")
    except getopt.GetoptError:
        print(sys.argv[0]+' -r flag_submit_request.txt -d db.db -p http -t sleep_time')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(sys.argv[0]+' -r flag_submit_request.txt -d db.db -p http -t sleep_time')
            sys.exit(2)
        elif opt in ("-r"):
            flag_submit_request_file = arg
        elif opt in ("-d"):
            db_file = arg
        elif opt in ("-p"):
            protocol = arg
        elif opt in ("-t"):
            sleep_time = int(arg)

    flag_auto_submit_class(db_file,protocol,flag_submit_request_file,sleep_time).run()

if __name__ == '__main__':
    main(sys.argv[1:])