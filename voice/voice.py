from threading import Thread

import pvporcupine
from pvrecorder import PvRecorder
from pyparrot.Bebop import Bebop

KEYWORDS = ["stop device"]


class PorcupineThread(Thread):
    def __init__(self, access_key, device_index, keyword_var):
        super().__init__()

        self._access_key = access_key
        self._device_index = device_index
        self._keyword_var = keyword_var

        self._is_ready = False
        self._stop = False
        self._is_stopped = False

    def run(self):
        ppn = None
        recorder = None

        try:
            ppn = \
                pvporcupine.create(access_key=self._access_key, keyword_paths=self._keyword_var)

            recorder = PvRecorder(device_index=self._device_index, frame_length=ppn.frame_length)
            recorder.start()

            self._is_ready = True

            while not self._stop:
                pcm = recorder.read()
                keyword_index = ppn.process(pcm)
                if keyword_index == 0:
                    print("drone stopped")
        finally:
            if recorder is not None:
                recorder.delete()

            if ppn is not None:
                ppn.delete()

        self._is_stopped = True

    def is_ready(self):
        return self._is_ready

    def stop(self):
        self._stop = True

    def is_stopped(self):
        return self._is_stopped


