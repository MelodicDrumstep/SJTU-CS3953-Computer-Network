import multiprocessing

class ProcessSafeHashMap:
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.hash_table = self.manager.dict()
        self.lock = multiprocessing.Lock()

    def put(self, key, value):
        with self.lock:
            self.hash_table[key] = value

    def get(self, key):
        with self.lock:
            return self.hash_table.get(key, None)

    def remove(self, key):
        with self.lock:
            if key in self.hash_table:
                del self.hash_table[key]

    def items(self):
        with self.lock:
            return list(self.hash_table.items())