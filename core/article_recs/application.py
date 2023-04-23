import logging
import threading
import schedule
import time
from article_recs import candidate_generator, content_extractor, crawler, recommender, crawler_reddit
from article_recs.context import Context
import uvicorn

from article_recs.web import Controller

def exception_handler_wrapper(callable):
    def wrapper(*args, **kwargs):
        try:
            callable(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
    return wrapper

def main():
    
    context = Context()
    
    schedule.every(2).hours.do(exception_handler_wrapper(lambda: crawler.main(context)))
    schedule.every(2).hours.do(exception_handler_wrapper(lambda: crawler_reddit.main(context)))
    schedule.every(3).minutes.do(exception_handler_wrapper(lambda: content_extractor.main(context)))
    schedule.every(10).minutes.do(exception_handler_wrapper(lambda: candidate_generator.main(context)))
    schedule.every(60).minutes.do(exception_handler_wrapper(lambda: recommender.main(context)))

    # start telegram target in the background thread
    threading.Thread(target=context.start_telegram_target).start()
    threading.Thread(target=run_pending).start()

    Controller(context)
    uvicorn.run(context.app, host="0.0.0.0", port=8000)

def run_pending():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()