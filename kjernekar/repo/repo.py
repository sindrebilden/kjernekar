import hashlib
import os
import json
import logging
import time
import urllib3
from threading import Thread, Event

class RepoWatcher(Thread):
    def __init__(self, repo_url=None, basic_auth=None, poll_interval=30, callback=None, alive=True):
        Thread.__init__(self)
        self.repo_url = repo_url
        self.basic_auth = basic_auth
        self.poll_interval = poll_interval
        self.callback = callback
        self.alive = alive

    def run(self):
        while self.alive:
            try:
                logging.debug('Pulling from repo {}'.format(self.repo_url))
                self.callback(self.fetch())
            
                for _ in range(self.poll_interval):
                    if self.alive:
                        time.sleep(1)
                    else:
                        return
            
            except KeyboardInterrupt:
                self.alive = False

    def fetch(self):
        http=urllib3.PoolManager()

        headers={
            'Authorization': 'Bearer {}'.format(self.basic_auth)
        }

        resp = http.request(
            'GET', 
            self.repo_url,
            headers=headers
        )

        return json.loads(resp.data.decode("utf-8"))['values']
        


if __name__ == "__main__":
    repo = RepoWatcher(
        repo_url=os.environ.get("REPOSITORY_URL"),
        basic_auth=os.environ.get("REPOSITORY_BASIC_AUTH"),
        poll_interval=5,
        callback=print
    )
    repo.start()