from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .customTg import TelegramBot

import json
import datetime
import asyncio
import websockets


### Form to push Task to Redis 
### {'data': {'type': 'task', 'user_id': user_id, 'time': timestamp, 'content': task}}


info_to_send = [
    [(datetime.datetime.now() + datetime.timedelta(minutes = 5)).timestamp(), 'Drink wine'],
    [(datetime.datetime.now() + datetime.timedelta(minutes = 10)).timestamp(), 'Drink coke'],
    [(datetime.datetime.now() + datetime.timedelta(minutes = 15)).timestamp(), 'Drink soda'],
    [(datetime.datetime.now() + datetime.timedelta(minutes = 20)).timestamp(), 'Drink water'],
    [(datetime.datetime.now() + datetime.timedelta(minutes = 25)).timestamp(), 'Drink coffee!!'],
]


async def new_redis_entry(user_id, time, content):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        dict_to_send = {'data': {'type': 'task', 'user_id': user_id, 'time': time, 'content': content}}
        await websocket.send(json.dumps(dict_to_send))
        print('Message to websocket is send!')
        status = await websocket.recv()
        print('Status', status)

async def send_message_to_websocket(message):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        dict_to_send = {'message': message}
        await websocket.send(json.dumps(dict_to_send))
        print('Message to websocket is send!')
        status = await websocket.recv()
        print('Status', status)


@method_decorator(csrf_exempt, name='dispatch')
class RemindMeApiView(View):
    tgBot = TelegramBot()

    def get(self, request, *args, **kwargs):
        print(request)
        return HttpResponse('<h1>Hello, RemindMe</h1>')


    def post(self, request, *args, **kwargs):
        
        request_body = json.loads(request.body)

        if 'from_redis' in request_body:
            user_id = request_body.get('chat_id')
            self.tgBot.sendMessage(user_id, 'Added new task')

        message = request_body.get('message')

        if message:
            user_id = message['chat'].get('id')
            task = request_body.get('text')
            #self.tgBot.sendMessage(user_id, 'Mirroring message')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.get_event_loop().run_until_complete(send_message_to_websocket(task))
            #new_redis_entry(user_id = user_id, time = info[0], content = info[1])
        print(json.loads(request.body))
        print(request.headers)
        print(datetime.datetime.now())
        return JsonResponse({'status_code': 200})

