import os
import time
from api import API
from summarizer import Summarizer

def process_events(api: API, summarizer: Summarizer):
    with api.load_events('content_summarizer', 'content_updated') as events:
        print(f'Processing {len(events)} events...')

        content_ids = []
        for e in events:
            if 'text' in e['fields']:
                content_ids.append(e['content_id'])
        
        for content in api.get_content(content_ids):
            data = content['data']
            if not data.get('text', None) is None:
                print(f'Summarizing {content["id"]}')
                summary = summarizer.summarize(data.get('text', None))
                print(f'Saving: {summary}')
                api.update_content(content["id"], {'summary': summary})

def main():
    api = API(os.environ["API_BASE_URL"])
    summarizer = Summarizer()

    while True:
        print('Processing events...')
        process_events(api, summarizer)
        time.sleep(5)


if __name__ == "__main__":
    main()