import asyncio
import importlib
import sys
import logging
import time

import aiohttp
from http2.request import Request
from http2.response import Response

spiderName = sys.argv[1]
mod = importlib.import_module(f'spiders.{spiderName}')
spider = mod.Spider()
done = set()

logging.basicConfig(level=logging.DEBUG)

headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}


async def fetch(url, session):
    logging.debug(f'下载 {url}')
    async with session.get(url, headers=headers) as resp:
        resp.raise_for_status()
        return await resp.text()


async def scheduler(request, queue):
        await queue.put(request)
        logging.debug(f'{request} 已被加入队列，当前队列有 {queue.qsize()} 个URL')

async def worker(id, queue, session):
    '''
        工作方式：
            * 从队列中取出 URL
            * 异步下载页面
            * 将下载结果返回给爬虫处理
            * 爬虫处理完返回URL或数据
            * 将URL加入队列；将数据交给管道处理
    '''
    while True:
        request = await queue.get()
        if request.fingerprint in done:
            logging.info(f'worker#{id} 过滤：{request.url} 已经采集过')
            queue.task_done() # 从队列获取元素并处理完之后，一定要调用 .task_done() 否则会造成阻塞
            continue
        done.add(request.fingerprint)
        logging.info(f'worker#{id} 将 {request} 从队列取出')
        # 等待响应
        resp = await fetch(request.url, session)
        resp = Response(request, resp)
        # 使用回调函数处理响应
        parse = getattr(request, 'callback')
        result = parse(resp) if parse else spider.parse(resp)
        # 回调函数返回新的URL或提取的数据
        for r in result:
            if isinstance(r, Request): # 新的URL
                logging.info(f'worker#{id} 将 {r} 加入队列')
                await scheduler(r, queue)
            else: # 提取的数据
                logging.info(f'Item:{r}')
        logging.info(f'worker#{id} 处理 {request} 完成')
        queue.task_done()

async def main():
    # 将URL种子放入队列
    queue = asyncio.Queue()
    initSeed = [scheduler(Request(url), queue) for url in spider.urls]
    await asyncio.gather(*initSeed)
    logging.info(f'qsize = {queue.qsize()}')

    # 启动爬虫，默认个数是 5
    workerNum = getattr(spider, 'workerNum', 5)
    logging.info(f'启动 {workerNum} 个worker')
    async with aiohttp.ClientSession() as session:
        for id in range(workerNum):
            asyncio.create_task(worker(id, queue, session))    
        await queue.join()    




if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main())
    print(f'\n {time.perf_counter()-start}s')