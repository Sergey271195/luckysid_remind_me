import asyncio
import requests
import websockets
import aioredis
import os
import json
import aiohttp
import random
import datetime
import functools

class AsyncTelegramListener():

    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.TOKEN = os.environ.get('REMINDME_TOKEN')
        self.URL = f'https://api.telegram.org/bot{self.TOKEN}'
        self.SEND_MESSAGE_URL = os.path.join(self.URL, 'sendMessage')
        self.MESSAGE_DELAY = 300 ### 5 minutes
        self.SEND_MESSAGE_INTERVAL = 120 ### 2 minutes before and after

    async def redis_connection_listener(self, request_interval):

        redis = await aioredis.create_redis_pool('redis://localhost', encoding="utf-8")
        while True:
            users = await redis.smembers('users')
            for user in users:
                closest_task = await redis.zpopmin(user)
                if closest_task:
                    time_delta =  int(closest_task[1]) - int(datetime.datetime.now().timestamp())
                    if abs(time_delta) < self.SEND_MESSAGE_INTERVAL:
                        print('Send message to user', user)
                        message_to_send = f'You asked us to remind you about: {closest_task[0][11:]}'
                        try:
                            async with self.session.post(self.SEND_MESSAGE_URL, data= {'chat_id': user, 'text': message_to_send}) as response:
                                print(response.status)
                                if response.status == 200:
                                    print('Success')
                                else:
                                    print(f'Message for user {user} was delayed')
                                    delay = int(closest_task[1]) + self.MESSAGE_DELAY
                                    await redis.zadd(user, delay, closest_task[0])
                        except Exception as e:
                            print(e)
                    elif time_delta < -200:
                        print('Delte unsend message. Time expired')
                    else:
                        await redis.zadd(user, int(closest_task[1]), closest_task[0])

            await asyncio.sleep(request_interval)

        redis.close()
        await redis.wait_closed()

    async def redis_manager(self, user_id, time, task):

        redis = await aioredis.create_redis_pool('redis://localhost')
        await redis.sadd('users', user_id)
        await redis.zadd(str(user_id), int(time), f'{int(time)}.{task}')
        redis.close()
        await redis.wait_closed() 


async def worker(queue):
    while not queue.empty():
        user_id, message = await queue.get()
        async with session.post(SEND_MESSAGE_URL, data= {'chat_id': user_id, 'text': message}) as response:
            r = await response.json()
            if response.status == 200:
                queue.task_done()
            else:
                await asyncio.sleep(10)
                await queue.put([user_id, message])



async def send_update_message(user_id, text):

    host_request = requests.post('http://127.0.0.1:8000/', json = {'from_redis': True, 'chat_id': user_id, 'text': text})
    print(host_request)

async def handle_message(queue):
    print('Outside', queue)
    await asyncio.sleep(10)
    while not queue.empty():
        print('Inside', queue)
        request = await queue.get()
        queue.task_done()

       
    
async def main(websocket, path, listener, message_queue):

        
        request = await websocket.recv()
        request_json = json.loads(request)
        data = request_json.get('data')
        if data:
            if data.get('type') == 'task':
                await listener.redis_manager(data.get('user_id'), data.get('time'), data.get('content'))
        else:
            await message_queue.put(request)
            print('Initial', message_queue)
            await handle_message(message_queue)

        await websocket.send('200')


if __name__ == '__main__':

    message_queue = asyncio.Queue()

    listener = AsyncTelegramListener()
    start_server = websockets.serve(functools.partial(main, listener=listener, message_queue = message_queue), "localhost", 8765)
    
    asyncio.get_event_loop().run_until_complete(asyncio.gather(listener.redis_connection_listener(5), start_server))
    asyncio.get_event_loop().run_forever()


""" await message_queue.put([data.get('user_id'), data.get('task')])
                loop = asyncio.get_event_loop()
                print(message_queue)
                task = loop.create_task(worker(message_queue))
                await task """