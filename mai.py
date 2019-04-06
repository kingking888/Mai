import asyncio
import importlib
import sys
import os
import logging
import time
from datetime import datetime
import pickle

import aiohttp
import redis
from http2.request import Request
from http2.response import Response
from core.stats import Counter
from core.mail import sendmail

spiderName = sys.argv[1]
batchId = sys.argv[2]
mod = importlib.import_module(f'spiders.{spiderName}')
spider = mod.Spider()

log = logging.getLogger('Mai')
log.setLevel(logging.DEBUG)
fmt = logging.Formatter(
    fmt='%(asctime)s %(name)s:%(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %X'
)
# 将警告和错误日志写入文件
os.makedirs('log', exist_ok=True)
filename = f'{spiderName}-{batchId}.log.txt'
logPath = os.path.join('.', 'log', filename)
fileHandler = logging.FileHandler(logPath, encoding='utf-8')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(fmt)
# 将普通日志输出到终端
consHandler = logging.StreamHandler()
consHandler.setLevel(logging.DEBUG)
consHandler.setFormatter(fmt)
## 
log.addHandler(fileHandler)
log.addHandler(consHandler)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}


async def fetch(request, session):
    log.debug(f'下载 {request.url}')
    async with session.get(request.url, headers=headers) as resp:
        resp.raise_for_status()
        text = await resp.text()
        return Response(request, text, resp.status)

async def scheduler(request, redisClient, urlQueue):
        redisClient.rpush(urlQueue, pickle.dumps(request))
        log.debug(f'{request} 已被加入队列，当前队列有 {redisClient.llen(urlQueue)} 个URL')

async def worker(id, urlQueue, urlDone,session, counter):
    '''
        工作方式：
            * 从队列中取出 URL
            * 异步下载页面
            * 将下载结果返回给爬虫处理
            * 爬虫处理完返回URL或数据
            * 将URL加入队列；将数据交给管道处理
    '''
    redisClient = redis.Redis()
    while redisClient.llen(urlQueue) > 0:
        request = pickle.loads(redisClient.brpop(urlQueue)[1])
        if redisClient.sismember(urlDone, request.fingerprint):
            log.info(f'worker#{id} 过滤：{request.url} 已经采集过')
            # queue.task_done() # 从队列获取元素并处理完之后，一定要调用 .task_done() 否则会造成阻塞
            continue
        redisClient.sadd(urlDone, request.fingerprint)
        log.info(f'worker#{id} 将 {request} 从队列取出')
        try: 
            resp = await fetch(request, session)
        except:
            counter.inc('badResponse', 1)
            log.exception(f'{request.url} 下载失败')
        else:
            counter.inc('response', 1)
            # 使用回调函数处理响应
            parse = getattr(request, 'callback')
            result = parse(resp) if parse else spider.parse(resp)
            # 回调函数返回新的URL或提取的数据
            for r in result:
                if isinstance(r, Request): # 新的URL
                    log.info(f'worker#{id} 将 {r} 加入队列')
                    await scheduler(r, redisClient, urlQueue)
                else: # 提取的数据
                    print(f'Item:{r}')
                    counter.inc('items', 1)
            log.info(f'worker#{id} 处理 {request} 完成')

async def main():
    counter = Counter()
    timefmt = '%Y-%m-%d %X'
    startTime = datetime.now()
    c = Counter()

    # 将URL种子放入队列
    # queue = asyncio.Queue()
    redisClient = redis.Redis()
    urlQueue = f'{spiderName}-{batchId}' 
    urlDone = f'{urlQueue}:done'
    initSeed = [scheduler(Request(url), redisClient, urlQueue) for url in spider.urls]
    await asyncio.gather(*initSeed)
    log.info(f'qsize = {redisClient.llen(urlQueue)}')

    # 启动爬虫，默认个数是 5
    workerNum = getattr(spider, 'workerNum', 5)
    workers = []
    log.info(f'启动 {workerNum} 个worker')
    async with aiohttp.ClientSession() as session:
        for id in range(workerNum):
            workers.append(asyncio.create_task(worker(id, urlQueue, urlDone, session, counter)))    
        # 阻塞知道所有URL处理完成
        await asyncio.gather(*workers)

    endtTime = datetime.now()
    stats = {
        'startTime': startTime.strftime(timefmt),
        'endtTime': endtTime.strftime(timefmt),
        'totalTime': str(endtTime - startTime),
    }
    stats.update(counter.get_counter())
    sendmail(spiderName, stats, logPath)
    log.info('\n' + '\n'.join([f'{k}: {v}' for k, v in stats.items()]))


if __name__ == "__main__":
    asyncio.run(main())
