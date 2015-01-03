import threading
import time


class Cache(object):

    STATE_READING = 0
    STATE_FINISHED = 1
    STATE_CANCELED = 2

    def __init__(self, fileobj, size, blocksize=2048):
        self._fileobj = fileobj
        self.size = size
        self._blocksize = blocksize
        self.state = self.STATE_READING
        self._memory = []
        self._current = 0
        self._active = True
        self.bytes_read = 0
        self._read_thread = threading.Thread(target=self._read)
        self._read_thread.start()

    def _read(self):
        data = self._fileobj.read(self._blocksize)
        while data and self._active:
            self._memory.append(data)
            self.bytes_read += len(data)
            data = self._fileobj.read(self._blocksize)
        if self._active:
            self.state = self.STATE_FINISHED
        self._fileobj.close()

    def reset(self):
        self._current = 0

    @property
    def offset(self):
        return self._current

    @offset.setter
    def offset(self, offset):
        self._current = offset

    def cancel(self):
        if self.state == self.STATE_READING:
            self._active = False
            self.state = self.STATE_CANCELED

    def read(self, size=None):
        start_block, start_bytes = divmod(self._current, self._blocksize)
        if size:
            if size > self.size - self._current:
                size = self.size - self._current
            while self._current + size > self.bytes_read:
                time.sleep(0.01)
            self._current += size
            end_block, end_bytes = divmod(self._current, self._blocksize)
            result = self._memory[start_block:end_block]
        else:
            while self.size > self.bytes_read:
                time.sleep(0.01)
            self._current = self.size
            result = self._memory[start_block:]
        if size:
            if end_bytes > 0 :
                result.append(self._memory[end_block][:end_bytes])
        if start_bytes > 0 and result:
            result[0] = result[0][start_bytes:]
        return b''.join(result)