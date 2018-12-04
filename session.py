#author: johnxguo
#date: 2018-10-31

import os
import aiohttp
import asyncio
import time
from speed import SpeedHelper

class Session:
    def __init__(self, cookies, headers, proxy = None):
        self.cacheSize = 3000000
        self.chuckSize = 1000000
        self.cookies = cookies
        self.headers = headers
        self.proxy = proxy
        self.session = asyncio.get_event_loop().run_until_complete(self.create_session(cookies, headers))

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    async def create_session(self, cookies, headers):
        return aiohttp.ClientSession(cookies=cookies, headers=headers, timeout=aiohttp.ClientTimeout(total=100000))

    async def get(self, url:str):
        async with self.session.get(url, proxy=self.proxy) as rsp:
            return await rsp.text()
    
    async def getWithHeaders(self, url:str, headers):
        headers = {**self.headers, **headers} 
        async with self.session.get(url, proxy=self.proxy, headers=headers) as rsp:
            return await rsp.text()

    async def post(self, url:str, data):
        async with self.session.post(url, data=data, proxy=self.proxy) as rsp:
            return await rsp.text()

    async def postWithHeaders(self, url:str, data, headers):
        headers = {**self.headers, **headers} 
        async with self.session.post(url, data=data, headers=headers, proxy=self.proxy) as rsp:
            return await rsp.text()

    async def fetch(self, url:str, path:str, handler:callable = None):
        tmpPath = path + '.tmp'
        try:
            if os.path.exists(path):
                return True
            with open(tmpPath, 'wb') as file:
                async with self.session.get(url, proxy=self.proxy) as rsp:
                    speedHelper = SpeedHelper(90, int(rsp.headers["Content-Length"]))
                    cache = bytes()
                    lastsize = 0
                    while 1:
                        chuck = await rsp.content.read(self.chuckSize)
                        if not chuck:
                            file.write(cache)
                            break
                        cache = cache + chuck
                        if len(cache) > self.cacheSize:
                            file.write(cache)
                            cache = bytes()
                        speedHelper.mark(len(chuck))
                        if handler:
                            size = speedHelper.size_done() - lastsize
                            lastsize = speedHelper.size_done()
                            handler(url, path, size, speedHelper.size_all(), speedHelper.size_done(), speedHelper.speed())
            os.rename(tmpPath, path)
            return True
        except Exception as err:
            print(err)
            return False
        finally:
            if os.path.exists(tmpPath):
                os.remove(tmpPath)
