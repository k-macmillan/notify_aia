# naia
Notify Asynchronous Internal API is primarily used to send external http requests. 

## Purpose
The "Notify" platforms across the globe ([CA](https://github.com/cds-snc/notification-api/blob/main/app/celery/service_callback_tasks.py), [UK](https://github.com/alphagov/notifications-api/blob/main/app/celery/service_callback_tasks.py), and the [US](https://github.com/department-of-veterans-affairs/notification-api/blob/master/app/celery/service_callback_tasks.py) for example) are using Celery to make external calls. In the US case they are also making [other](https://github.com/department-of-veterans-affairs/notification-api/blob/master/app/celery/lookup_va_profile_id_task.py) external [calls](https://github.com/department-of-veterans-affairs/notification-api/blob/master/app/celery/contact_information_tasks.py).

Web requests average a couple hundred milliseconds of wasted time for each task; sometimes it can take significantly longer. Every one of these requests holds a Celery worker hostage while waiting for the request to finish. Celery tasks can make the requests, but Celery does not play nice with asynchronous calls to [aiohttp](https://github.com/aio-libs/aiohttp).

This allows compute-focused tasks to use Celery, and IO-bound tasks to use the asynchronous API. 
