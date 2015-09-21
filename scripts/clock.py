from __future__ import print_function

from django.core.management import call_command

from apscheduler.schedulers.blocking import BlockingScheduler

from bedrock.events.cron import cleanup_ical_events, update_ical_feeds
from bedrock.mozorg.cron import update_tweets
from scripts import update_firefox_os_feeds, update_tableau_data


schedule = BlockingScheduler()


class scheduled_job(object):
    """Decorator for scheduled jobs. Takes same args as apscheduler.schedule_job."""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, fn):
        job_name = fn.__name__
        self.name = job_name
        self.callback = fn
        schedule.add_job(self.run, id=job_name, *self.args, **self.kwargs)
        return self.run

    def run(self):
        self.log('starting')
        try:
            self.callback()
        except Exception as e:
            self.log('CRASHED: {}'.format(e))
            raise
        else:
            self.log('finished successfully')

    def log(self, message):
        print('Clock job {0}: {1}'.format(self.name, message))


@scheduled_job('interval', seconds=5)
def job_should_pass():
    print('DO ALL THE THINGS!!!')


@scheduled_job('interval', seconds=5)
def job_raise_exception():
    raise ValueError("Stuff's broke yo!")


@scheduled_job('interval', minutes=30)
def job_update_externalfiles():
    call_command('update_externalfiles')


@scheduled_job('interval', minutes=30)
def job_update_security_advisories():
    call_command('update_security_advisories')


@scheduled_job('interval', minutes=5)
def job_rnasync():
    call_command('rnasync')


@scheduled_job('interval', hours=6)
def job_update_tweets():
    update_tweets()


@scheduled_job('interval', hours=1)
def job_ical_feeds():
    update_ical_feeds()
    cleanup_ical_events()


@scheduled_job('interval', hours=1)
def job_update_firefox_os_feeds():
    update_firefox_os_feeds.run()


@scheduled_job('cron', day_of_week='sat', hour=0)
def job_update_tableau_data():
    update_tableau_data.run()


def run():
    try:
        schedule.start()
    except (KeyboardInterrupt, SystemExit):
        pass
