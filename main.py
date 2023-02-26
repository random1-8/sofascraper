import argparse
import config
import excel
import sofa
from datetime import date, datetime, timedelta


parser = argparse.ArgumentParser(description='Sofascore football scraper')
parser.add_argument("-v", "--verbose", action="store_true", help="increase verbosity")
#args = parser.parse_args()
#config = vars(args)

## Create and configure logger
#logging.basicConfig(filename="newfile.log", format='%(asctime)s %(message)s', filemode='w')
#
## Creating an object
#logger = logging.getLogger()
#
## Setting the threshold of logger
#if config['verbose']:
#    logger.setLevel(logging.DEBUG)
#else:
#    logger.setLevel(logging.INFO)

#matchday = date.today() - timedelta(days=1) # Yesterday's matches? Feel free to change to whenever you want

need_browser = False

if need_browser:
    config.start_browser()
    #from_date = datetime.fromisoformat('2022-08-01')
    #sofa.unique_tournament(8,  from_date)
    #sofa.unique_tournament(17, from_date)
    #sofa.unique_tournament(18, from_date)
    #sofa.unique_tournament(23, from_date)
    #sofa.unique_tournament(34, from_date)
    #sofa.unique_tournament(35, from_date)
    config.quit_browser()

excel.create_from_teams([4778, 4715])