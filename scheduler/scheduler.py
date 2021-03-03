from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from loguru import logger
import sys


class Scheduler():


    def schedulerGenerator(self):
            try:
                jobstores = {
                    'mongo': {'type': 'mongodb'},
                    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
                }
                executors = {
                    'default': {'type': 'threadpool', 'max_workers': 20},
                    'processpool': ProcessPoolExecutor(max_workers=5)
                }
                job_defaults = {
                    'coalesce': True,
                    'max_instances': 1
                }
                scheduler = BlockingScheduler(daemon=True)
                return scheduler
            except :
                logger.warning('Scheduler konnte nicht initialisiert werden: ' + str(sys.exc_info()[1]))




