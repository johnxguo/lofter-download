#coding:utf-8
import sys, urllib, requests, gzip, io, re, os, socket, shutil

#lofter原图是只保存八个月的
#另外rss页面也可以参考一下，更简单直接，http://t95821704.lofter.com/rss?p=2

socket.setdefaulttimeout(30)

regBlogId = 'blogId=(.+?)\"'
reBlogIdCpl = re.compile(regBlogId)

regAlbumId = 'permalink=\"(.+?)\"'
reAlbumIdCpl = re.compile(regAlbumId)

regImg = 'bigimgsrc=\"(.+?)[\?\"]'
reImgCpl = re.compile(regImg)

def getFileName(url):
    return requests.utils.unquote(url).split('/')[-1]

def getUrl(url):
    doc = requests.get(url)
    return doc.text

def postUrl(url, headers, params):
    data = urllib.parse.urlencode(params)
    response = requests.post(url=url, data=params, headers=headers)
    ret = ''
    return response.content.decode('utf-8')

def downLoadImage(url, retry):
    print(imgUrl + "  " + str(retry))
    try:
        urllib.request.urlretrieve(imgUrl, albumPath + '_' + getFileName(imgUrl))
    except IOError as e:
        if retry > 0:
            retry = retry - 1;
            downLoadImage(url, retry)
        else:
            return
            
def isDone(albumId):
    for id in doneList:
        if id == albumId:
            return True
    return False
        
def loadDoneList():
    if not os.path.isfile(targetName + "/donelist.txt"):
        return
    for line in open(targetName + "/donelist.txt"):
        doneList.append(line.rstrip('\n'))
    
def createUnDone():
    f = open(targetName + "/undone", "w")
    f.write("undone")
    f.close()
        
def removeUnDone():
    if os.path.isfile(targetName + "/undone"):
        os.remove(targetName + "/undone")
    
def onDone(albumId):
    f = open(targetName + "/donelist.txt", "a+")
    f.writelines(albumId + "\n")
    f.close()
    doneList.append(albumId)

#------------------------------------------------------------

params = {
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

headers = { 
  'Accept-Encoding':'gzip',
  'Referer':''
}  

doneList = []

if len(sys.argv) <= 1:
    print("输入目标用户名")
    exit()

targetName = sys.argv[1]
targetMain = "http://" + targetName + ".lofter.com"
targetView = "http://" + targetName + ".lofter.com/view"
targetPageList = "http://" + targetName + ".lofter.com/dwr/call/plaincall/ArchiveBean.getArchivePostByTime.dwr"
albumPrefix = "http://ada86t.lofter.com/post/"
headers['Referer'] = targetView

if not os.path.exists(targetName):
    os.mkdir(targetName)
print(targetMain)

removeUnDone()

mainHtml = getUrl(targetMain)
idList = re.findall(reBlogIdCpl, mainHtml)
if (len(idList) == 0):
    exit()
blogId = idList[0]
print(blogId)

loadDoneList()
createUnDone()

params['c0-param1'] = 'number:' + blogId

doc = postUrl(targetPageList, headers, params)
albumIdList = re.findall(reAlbumIdCpl, doc)
print(albumIdList)

size = len(albumIdList)
cur = 0

for albumId in albumIdList:
    print(albumId + "  " + str(cur) + "/" + str(size))
    cur += 1
    albumPath = targetName + "/" + albumId
    if isDone(albumId=albumId):
        continue
    albumUrl = albumPrefix + albumId
    albumHtml = getUrl(albumUrl)
    imgList = re.findall(reImgCpl, albumHtml)
    print("共" + str(len(imgList)) + "张")
    for imgUrl in imgList:
        downLoadImage(imgUrl, 5)
    onDone(albumId=albumId)
    
removeUnDone()
    
    
    
    
    
    
    
