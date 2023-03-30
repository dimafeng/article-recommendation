import requests
from typing import List

class EventReader(object):
    def __init__(self, base_url: str, consumer_id: str, event_type: str):
        self.base_url = base_url
        self.consumer_id = consumer_id
        self.event_type = event_type

    def __enter__(self):
        self.request = requests.get(
            self.base_url + 
            f'/events?consumer_id={self.consumer_id}&event_type={self.event_type}&limit=50').json()
        return  [event['data'] for event in self.request]
 
    def __checkpoint(self, checkpoint: int):
        requests.post(self.base_url + '/events/checkpoint', json={
            'consumer_id': self.consumer_id,
            'event_type': self.event_type,
            'checkpoint': checkpoint
        })

    def __exit__(self, *args):
        last_event = self.request[-1]
        self.__checkpoint(last_event['id'])

class API():
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def load_events(self, consumer_id: str, event_type: str) -> EventReader:
        return EventReader(self.base_url, consumer_id, event_type)
        
    def update_content(self, content_id: str, data: dict):
        requests.post(self.base_url + '/contents/update', json={
            'content_id': content_id,
            'data': data
        })

    def get_content(self, content_ids: List[str]) -> dict:
        request = requests.get(self.base_url + f'/contents?content_ids={",".join(content_ids)}')
        return request.json()

