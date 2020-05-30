import os, requests, sys, io
import subprocess
import speech_recognition as sr


class TelegramSpeechRecognizer():

    def __init__(self, file_id, token):
        self.file_id = file_id
        self.token = token
        self.file_path = f'https://api.telegram.org/{self.token}/getFile?file_id={self.file_id}'
        self.download_link = self.get_data()

    def get_data(self):

        r = requests.get(self.file_path)
        result = r.json()
        url = result['result'].get('file_path')
        download_link = f'https://api.telegram.org/file/{self.token}/{url}'
        return download_link

    def convert_data(self):

        process = subprocess.Popen(['ffmpeg', '-i', self.download_link, '-f', 'wav', '-'], stdout = subprocess.PIPE)
        bytes_data = process.stdout.read()

        audio_data = sr.AudioData(bytes_data, 48000, 2)
        recognizer = sr.Recognizer()
        try:
            transcribed_data = recognizer.recognize_google(audio_data, language = 'ru-RU')
            print("Google Speech Recognition thinks you said " + transcribed_data)
            return(transcribed_data)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return(None)
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return(None)


mess = notification.get('message')
if mess:
    voice = mess.get('voice')
    if voice:
        file_id = voice.get('file_id')

        tsr = TelegramSpeechRecognizer(file_id, os.environ.get('LAVANDA_TOKEN'))
        response = tsr.convert_data()
        if response:
            if any([voice_command in response.lower() for voice_command in VOICE_COMMANDS]):
                if VOICE_COMMANDS[0] in response.lower():
                    self.tgBot.sendMessage(user.telegram_id, f"Привет, {user.first_name}")
                if VOICE_COMMANDS[1] in response.lower():
                    self.tgBot.sendMessage(user.telegram_id, f"Сейчас {datetime.datetime.now().strftime('%H:%M:%S')}")
                if VOICE_COMMANDS[2] in response.lower():
                    self.tgBot.sendMessage(user.telegram_id, f"Мои создатели еще не придумали мне имя")
                if VOICE_COMMANDS[3] in response.lower():
                    self.tgBot.sendMessage(user.telegram_id, f"Пока, {user.first_name}")
            else:
                self.tgBot.sendMessage(user.telegram_id, f"Google Speech Recognition считает, что ты сказал: {response}")
        else:
            self.tgBot.sendMessage(user.telegram_id, f"Google Speech Recognition could not understand audio")