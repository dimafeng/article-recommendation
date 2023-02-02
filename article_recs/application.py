import logging
import threading
import schedule
import time
from article_recs import candidate_generator, content_extractor, crawler, recommender, crawler_reddit
from article_recs.context import Context


def main():
    
    context = Context()
    # schedule.every(10).seconds.do(lambda: crawler.main(context))
    # schedule.every(10).seconds.do(lambda: crawler_reddit.main(context))
    # schedule.every(10).seconds.do(lambda: content_extractor.main(context))
    # schedule.every(10).seconds.do(lambda: candidate_generator.main(context))
    # schedule.every(10).seconds.do(lambda: recommender.main(context))

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    context.start_telegram_target()

if __name__ == "__main__":
    main()