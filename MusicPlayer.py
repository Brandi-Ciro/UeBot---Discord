import requests
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio


class MusicPlayer:

    def __init__(self, bot):
        self._isStopped = False
        self._queue = list()
        self._bot = bot
        self._ctx = None
        self._voiceClient = None
        self._ffmpegOpts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                            'options': '-vn'}

    @property
    def ffmpegOpts(self):
        return self._ffmpegOpts

    @property
    def queue(self):
        return self._queue

    @property
    def ctx(self):
        return self._ctx

    @ctx.setter
    def ctx(self, value):
        self._ctx = value

    @property
    def isStopped(self):
        return self._isStopped

    @isStopped.setter
    def isStopped(self, value):
        self._isStopped = value

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

    @property
    def voiceClient(self):
        return self._voiceClient

    @voiceClient.setter
    def voiceClient(self, value):
        self._voiceClient = value

    def search(self, query: str):
        with YoutubeDL({'noplaylist': 'True'}) as ydl:
            try:
                requests.get(query)
            except:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            else:
                info = ydl.extract_info(query, download=False)
        return info, info['formats'][0]['url']

    def add_song(self, url: str):
        self._queue.append(url)

    def remove_song(self):
        if not self.queue_is_empty():
            self._queue.pop(0)

    def clear_queue(self):
        self._queue = list()

    def queue_is_empty(self):
        return len(self._queue) == 0

    def play_song(self, url: str):
        voice = self._voiceClient
        video, source = self.search(url)
        if not voice.is_playing():
            voice.play(FFmpegPCMAudio(source, **self._ffmpegOpts), after=self.play_next_song)
            self._ctx.send(f'Playing {url}')
            self.remove_song()

    def play_next_song(self, error):
        if not self.isStopped:
            if not self.queue_is_empty():
                self.play_song(self.queue[0])
        else:
            self.isStopped = False
