#author: johnxguo
#date: 2018-12-5

import sys
import urllib
import requests
import io
import re
import os
import shutil
import asyncio
from session import Session

class LofterDownloader:
    def __init__(self, target, workpath):
        self.target = target
        self.workpath = workpath
        self.maxTaskNum = 7
        self.curTaskNum = 0
        self.totalCount = 0
        self.doneCount = 0
        self.targetpath = self.workpath + self.target + '/'
        self.donelist = []
        self.initUrls()
        self.initData()
        self.initRegular()
        self.initSession()
        self.asyncrun(self.start())

    def initUrls(self):
        self.targetMain  = "http://" + self.target + ".lofter.com"
        self.targetView  = "http://" + self.target + ".lofter.com/view"
        self.targetPglst = "http://" + self.target + ".lofter.com/dwr/call/plaincall/ArchiveBean.getArchivePostByTime.dwr"
        self.albumPrefix = "http://" + self.target + ".lofter.com/post/"

    def initRegular(self):
        self.reBlogIdCpl  = re.compile('blogId=(.+?)\"')
        self.reAlbumIdCpl = re.compile('permalink=\"(.+?)\"')
        self.reImgCpl     = re.compile('bigimgsrc=\"(.+?)[\?\"]')

    def initSession(self):
        headers = {
            'Accept-Encoding': 'gzip',
            'Referer': self.targetView
        }
        self.session = Session(None, headers)

    def initData(self):
        self.data = {
            'callCount':'1',
            'scriptSessionId':'187',
            'c0-scriptName':'ArchiveBean',
            'c0-methodName':'getArchivePostByTime',
            'c0-id':'0',
            'c0-param0':'boolean:false',
            'c0-param1':'number:1794082',
            'c0-param2':'number:1543936262219',
            'c0-param3':'number:5000',
            'c0-param4':'boolean:false',
            'batchId':'366472'
        }
    
    def asyncrun(self, future):
        return asyncio.get_event_loop().run_until_complete(future)

    async def start(self):
        if not os.path.exists(self.targetpath):
            os.mkdir(self.targetpath)
        print(self.targetpath)
        
        self.removeUndone()

        mainHtml = await self.get(self.targetMain)
        idList = re.findall(self.reBlogIdCpl, mainHtml)
        if (len(idList) == 0):
            return
        blogId = idList[0]
        print(blogId)

        self.loadDonelist()
        self.createUndone()

        doc = await self.post(self.targetPglst, {'c0-param1':'number:' + blogId})
        albumIdList = re.findall(self.reAlbumIdCpl, doc)
        print(albumIdList)

        self.totalCount = len(albumIdList)
        tasks = [asyncio.ensure_future(self.fuckAlbum(albumId)) for albumId in albumIdList]
        await asyncio.wait(tasks)
            
        self.removeUndone()
    
    async def fuckAlbum(self, albumId):
        while self.curTaskNum >= self.maxTaskNum:
            await asyncio.sleep(3)
        self.curTaskNum += 1
        albumPath = targetName + "/" + albumId
        if self.isDone(albumId=albumId):
            self.doneCount += 1
            self.curTaskNum -= 1
            print(albumId + " is done")
            return
        albumUrl = self.albumPrefix + albumId
        albumHtml = await self.get(albumUrl)
        imgList = re.findall(self.reImgCpl, albumHtml)
        print(albumId + " 共" + str(len(imgList)) + "张, " + str(self.doneCount) + "/" + str(self.totalCount))
        if len(imgList) > 0:
            tasks = [asyncio.ensure_future(self.download(imgUrl, albumPath, 5)) for imgUrl in imgList]
            await asyncio.wait(tasks)
            if self.isResultSucc(tasks):
                self.onDone(albumId=albumId)
        self.doneCount += 1
        self.curTaskNum -= 1
            
    def isResultSucc(self, tasks):
        return len([task for task in tasks if not task.result()]) == 0

    def getUrlFileName(self, url):
        return requests.utils.unquote(url).split('/')[-1]

    async def get(self, url):
        return await self.session.get(url)

    async def post(self, url, data):
        data = {**self.data, **data}
        return await self.session.post(url, data)

    async def download(self, url, albumPath, retry):
        print(url + "  " + str(retry))
        path = albumPath + '_' + self.getUrlFileName(url)
        return await self.session.fetch(url, path)
            
    def isDone(self, albumId):
        for id in self.donelist:
            if id == albumId:
                return True
        return False
        
    def loadDonelist(self):
        self.donelist.clear()
        if not os.path.isfile(targetName + "/donelist.txt"):
            return
        for line in open(targetName + "/donelist.txt"):
            self.donelist.append(line.rstrip('\n'))
    
    def createUndone(self):
        with open(targetName + "/undone", "w") as f:
            f.write("undone")
            
    def removeUndone(self):
        if os.path.isfile(targetName + "/undone"):
            os.remove(targetName + "/undone")
        
    def onDone(self, albumId):
        with open(targetName + "/donelist.txt", "a+") as f:
            f.writelines(albumId + "\n")
        self.donelist.append(albumId)

if len(sys.argv) <= 1:
    print("输入目标用户名")
    exit()

targetName = sys.argv[1]

LofterDownloader(targetName, './')
