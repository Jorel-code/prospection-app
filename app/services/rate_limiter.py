import time
import threading

class RateLimiter:
    def __init__(self, max_appels, periode_secondes):
        self.max_appels = max_appels
        self.periode = periode_secondes
        self.appels = []
        self.lock = threading.Lock()

    def wait_if_needed(self):
        with self.lock:
            maintenant = time.time()
            self.appels = [t for t in self.appels if maintenant - t < self.periode]
            if len(self.appels) >= self.max_appels:
                temps_attente = self.periode - (maintenant - self.appels[0])
                time.sleep(max(0, temps_attente))
            self.appels.append(time.time())