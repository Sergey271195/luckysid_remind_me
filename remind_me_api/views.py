from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import datetime
import asyncio
import websockets, os

if os.environ.get('DEBUG') == 'True':
    websocket_uri = "ws://localhost:8765" 
else:
    websocket_uri = 'wss://remindme-scheduler.herokuapp.com/0.0.0.0'


async def new_redis_entry(user_id, time, content):
    uri = websocket_uri
    async with websockets.connect(uri) as websocket:
        dict_to_send = {'data': {'type': 'task', 'user_id': user_id, 'time': time, 'content': content}}
        await websocket.send(json.dumps(dict_to_send))
        print('Message to websocket is sent!')
        status = await websocket.recv()
        print('Status', status)

async def send_voice_message_to_websocket(user_id, file_id):
    uri = websocket_uri
    async with websockets.connect(uri) as websocket:
        dict_to_send = {'data': {'type': 'voice', 'user_id': user_id, 'file_id': file_id}}
        await websocket.send(json.dumps(dict_to_send))
        print('Voice message to websocket is sent!')
        status = await websocket.recv()
        print('Status', status)

async def send_message_to_websocket(user_id, message):
    uri = websocket_uri
    async with websockets.connect(uri) as websocket:
        dict_to_send = {'data': {'type':'message', 'user_id': user_id, 'message': message}}
        await websocket.send(json.dumps(dict_to_send))
        print('Message to websocket is sent!')
        status = await websocket.recv()
        print('Status', status)

async def send_reply_message_to_websocket(user_id, message):
    uri = websocket_uri
    async with websockets.connect(uri) as websocket:
        dict_to_send = {'data': {'type':'reply_message', 'user_id': user_id, 'message': message}}
        await websocket.send(json.dumps(dict_to_send))
        print('Message to websocket is sent!')
        status = await websocket.recv()
        print('Status', status)


@method_decorator(csrf_exempt, name='dispatch')
class RemindMeApiView(View):

    def get(self, request, *args, **kwargs):
        print(request)
        return HttpResponse('<h1>Hello, RemindMe</h1>')


    def post(self, request, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        request_body = json.loads(request.body)
        print(request_body)
        message = request_body.get('message')
        callback_query = request_body.get('callback_query')

        print(message)

        if message:
            user_id = message['chat'].get('id')
            if message.get('voice'):
                file_id = message['voice'].get('file_id')
                asyncio.get_event_loop().run_until_complete(send_voice_message_to_websocket(user_id, file_id))
            else:
                task = request_body.get('text')              
                asyncio.get_event_loop().run_until_complete(send_message_to_websocket(user_id, task))

        elif callback_query:
            user_id = callback_query['message']['chat'].get('id')
            reply_to_message = callback_query['message']['text']
            if 'Set' in reply_to_message:
                data = callback_query['data']
                if data != 'no':
                    asyncio.get_event_loop().run_until_complete(send_reply_message_to_websocket(user_id, 'add.'+data))
            elif 'Alter' in reply_to_message:
                data = callback_query['data']
                if data != 'no':
                    asyncio.get_event_loop().run_until_complete(send_reply_message_to_websocket(user_id, 'alter.'+data))
            elif 'Delete' in reply_to_message:
                data = callback_query['data']
                if data != 'no':
                    asyncio.get_event_loop().run_until_complete(send_reply_message_to_websocket(user_id, 'remove.'+data))
            elif 'Shift' in reply_to_message:
                data = callback_query['data']
                if data != 'no':
                    asyncio.get_event_loop().run_until_complete(send_reply_message_to_websocket(user_id, 'move.'+data))



        return JsonResponse({'status_code': 200})

