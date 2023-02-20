import logging
import threading
import schedule
import time
from article_recs import candidate_generator, content_extractor, crawler, recommender, crawler_reddit
from article_recs.context import Context


def main():
    
    context = Context()
    
    schedule.every(2).hours.do(lambda: crawler.main(context))
    schedule.every(2).hours.do(lambda: crawler_reddit.main(context))
    schedule.every(10).minutes.do(lambda: content_extractor.main(context))
    schedule.every(10).minutes.do(lambda: candidate_generator.main(context))
    schedule.every(60).minutes.do(lambda: recommender.main(context))

    # start telegram target in the background thread
    threading.Thread(target=context.start_telegram_target).start()
 
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()