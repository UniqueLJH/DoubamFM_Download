#-*- coding: utf-8 -*-
import requests
import re
import json
import os
import sys
import random
import string
import time
import platform
class DoubanFM(object):
    def __init__(self,user_name,user_password):
        self.user_name = user_name
        self.user_password = user_password
        self.s = requests.Session()
        if platform.system()=='Windows':
            self.charset = 'gbk'
        else:
            self.charset = 'utf-8'

    def get_captcha(self):
        r = self.s.get("http://www.douban.com/service/account/check_with_js")
        st1 =self.s.get("http://douban.fm/j/misc/login_form")
        st2 =self.s.get("http://douban.fm/j/new_captcha")
        self.usercookie = st1.cookies['bid']
        #print self.usercookie
        #print st1.url
        #print st2.text #captcha_ID
        self.captcha_id = st2.text.strip('"')
        #print self.captcha_id
        captcha_url = "http://douban.fm/misc/captcha?size=m&id="+st2.text.strip('"')
        #print captcha_url
        #print st2.cookies['bid']
        captchaweb = self.s.get(captcha_url)
        #print captchaweb.content
        pic = open("pic.jpg","wb")
        pic.write(captchaweb.content)
        pic.close()
        self.captcha=raw_input('iuput the captcha in pic.jpg:')

    def login_web(self):
        login_url = 'http://douban.fm/j/login'
        self.data = {'source':'radio',
                'alias':self.user_name,
                'form_password':self.user_password,
                'captcha_solution':self.captcha,
                'captcha_id':self.captcha_id,
                'task':'sync_channel_list'
                }
        self.cookie = {'bid':self.usercookie,
                '__utma':'58778424.1481704969.1396472106.1397939124.1398286075.7',
                '__utmz':'58778424.1396472106.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
                'fmNlogin':'"y"',
                '__utmb':'58778424.12.9.1398287235460',
                'flag':'"ok"',
                'ac':'"1398257676"',
                '__utmc':'58778424'
                }

        login = self.s.post("http://douban.fm/j/login",data = self.data,cookies=self.cookie)
        #print login.content
        num = json.loads(login.content)
        self.like = num['user_info']['play_record']['liked']
        print 'the number of your songs is %s' % self.like

    def get_list(self,channel):
        songdict = {}
        numsong = 0
        getnum = 0
        aimnum = int(raw_input('plz input the number of songs U wanna get:'))
        print 'start to get %d songs' % aimnum
        #while 1.0*numsong<0.95*like:
        try:
            while numsong<aimnum:
                sid = str(random.randint(1000000,1999999))
                pt = str(round(150.0*random.random(),1))
                r = ''.join([('abcdef'+string.digits)[x] for x in random.sample(range(0,16),10)])
                list_url = 'http://douban.fm/j/mine/playlist?type=n&channel='+str(channel)+'&sid='+sid+'&pt='+pt+'&pb=64&from=mainsite&r='+r
                getlikelist = self.s.get(list_url,cookies=self.cookie)
                #print getlikelist.content
                d = json.loads(getlikelist.content)
                for data in d['song']:
                    songtitle = data['title'].encode(self.charset)
                    songartist = data['artist'].encode(self.charset)
                    songurl =data['url']
                    if (songdict.has_key(songtitle+'-*-'+songartist)== False)and(numsong<aimnum):
                        newsong = {songtitle+'-*-'+songartist:songurl}
                        #print newsong
                        songdict.update(newsong)
                        numsong = numsong + 1
                print 'the %dth get,it had got %d songs,wait..'% (getnum,numsong)
                getnum = getnum +1
                time.sleep(random.randint(3,7))

        finally:
            print numsong
            file1 =open("songlist.txt","wb")
            for key in songdict:
                if songdict[key].find('.flv')== -1:
                    file1.write(key+'-*-'+songdict[key].encode(self.charset)+'\n')
            file1.close()
           # file2 = open("test.mp4","w")
    def download(self):
        cwd = os.getcwd()
       # if platform.system()=='Windows':
         #   mp3load = r''+cwd+'\\mp3'
         #   fileload = r''+mp3load+'\\'
    #    else:
        mp3load = cwd+'/mp3'
        fileload = mp3load+'/'
        isExists = os.path.exists(mp3load)
        if not isExists:
            os.makedirs(mp3load)
        file1 = open('songlist.txt')
        st = file1.readlines()
        print fileload
        for index,line in enumerate(st):
            songname,artist,url = line.strip().split('-*-')
            isEx = os.path.exists(fileload+songname+'mp3')
            if not isEx:
                try:
                    
                    print 'Download %s' %songname
                    r = requests.get(url)
                    file2 = open(fileload+songname+'.mp3','wb')
                    file2.write(r.content)
                    file2.close()
                    print 'Complete %s' %songname
                except:
                    print 'Error in Download %s' %songname
            else :
                print 'Complete %s' %songname
        print 'All Complete quit after 20s'
        time.sleep(20)

#if len(sys.argv)<2:
    #print 'Useage:doubanFM.py user_name user_password'
    #sys.exit(0)
ua = raw_input("Username:")
up = raw_input("password:")
a = DoubanFM(ua,up)
a.get_captcha()
a.login_web()
a.get_list(-3)
a.download()

