import os
import time
from api import API
from autogluon.tabular import TabularDataset, TabularPredictor
import pandas as pd
import json
from urllib.parse import urlparse

features = ['id','domain', 'source', 'title', 'text', 'authors', 
                           'summary', 'top_image_exists', 
                           'publish_date', 'hackernews_type', 'hackernews_score', 
                           'hackernews_publish_datetime']
features_train = features + ['vote']

def content_to_dict(content):
    data = content['data']
    return {
            'id': content['id'],
            'domain': urlparse(content.get('url',None)).netloc,
            'source': urlparse(content.get('source',None)).netloc,
            'title': data.get('title',content.get('title', None)), 
            'text': data.get('text',None), 
            'authors':  ' '.join(data.get('authors', [])),
            'summary': data.get('summary', None),
            'top_image_exists': not (not data.get('top_image', None)),
            'publish_date': data.get('publish_date', None),
            'hackernews_type': data['hackernews_data']['type'] if data.get('hackernews_data', None) else None,
            'hackernews_score': data['hackernews_data']['score'] if data.get('hackernews_data', None) else None,
            'hackernews_publish_datetime': data['hackernews_data']['time'] if data.get('hackernews_data', None) else None
        }

def training_data(api: API):
    df = pd.DataFrame(columns=features_train)

    page = 0
    while True:
        print(f'reading page {page}')
        signals = api.get_signals(page, 50)
        
        if len(signals) == 0:
            break

        content_signals = [ x['data'] for x in signals if x['signal_type'] == 'vote' ]
        content_signal_map = {x['data']['content_id']: x['data']['vote'] for x in signals if x['signal_type'] == 'vote'}

        for content in api.get_content([x['content_id'] for x in content_signals]):

            vote = content_signal_map[content['id']]
            
            row_dict = content_to_dict(content)
            row_dict['vote'] = 1 if vote == 'fire' or vote == 'up' else 0

            df.loc[len(df)] = row_dict
        
        page = page + 1
    
    return df

def train(api: API) -> TabularPredictor:
    print('Training...')
    
    df = training_data(api)

    label = 'vote'
    print("Summary of class variable: \n", df[label].describe())

    return TabularPredictor(label=label).fit(df)

def predict(api: API, predictor: TabularPredictor):
    print('Predicting...')
    df = pd.DataFrame(columns=features)

    page = 0
    while page < 10:
        print(f'reading page {page}')
        candidates = api.get_candidates(page, 50)
        
        if len(candidates) == 0:
            break
            
        for content in api.get_content([x['content_id'] for x in candidates]):   
            row_dict = content_to_dict(content)

            df.loc[len(df)] = row_dict
        
        page = page + 1

    y_pred = predictor.predict_proba(df)

    df['score'] = y_pred[1].values

    return df

def process_predictions(api: API, df: pd.DataFrame):
    print(f'Processing {len(df)} events...')
    for index, row in df.iterrows():
        print(f'Updating {row["id"]}')
        api.update_candidates(row['id'], {'similarity_score': row['score']})

def main():
    api = API(os.environ["API_BASE_URL"])

    while True:
        print('Processing events...')
        predictor = train(api)
        prediction = predict(api, predictor)
        process_predictions(api, prediction)
        time.sleep(60*10)


if __name__ == "__main__":
    main()