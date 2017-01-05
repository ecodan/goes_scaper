from scraper import GoesScraper

import schedule
import time

print('creating scraper...')
scraper = GoesScraper()

print('setting schedule...')
schedule.every().day.at('08:00').do(scraper.run)
schedule.every().day.at('10:00').do(scraper.run)
schedule.every().day.at('12:00').do(scraper.run)
schedule.every().day.at('13:00').do(scraper.run)
schedule.every().day.at('14:00').do(scraper.run)
schedule.every().day.at('15:00').do(scraper.run)
schedule.every().day.at('16:00').do(scraper.run)
schedule.every().day.at('17:00').do(scraper.run)
schedule.every().day.at('18:00').do(scraper.run)
schedule.every().day.at('19:00').do(scraper.run)
schedule.every().day.at('20:00').do(scraper.run)
schedule.every().day.at('21:00').do(scraper.run)
schedule.every().day.at('22:00').do(scraper.run)

print('starting run loop...')
while 1:
    schedule.run_pending()
    time.sleep(60)

print('done - exiting')