Sked
====

Sked lets you solve the problem of "I have all these calendars and I want to share (some) of them with other people". It lets you take any combination of Google calendars and arbitrary other [iCalendar](https://en.wikipedia.org/wiki/ICalendar) feeds and make new feeds that you can then share with people. You can also only share the "I'm busy" data from a calendar, instead of it's full data if you want.

Once you've given someone one of these new feeds, you can always update their permissions afterwards - this means if you add new calendars, you don't need to tell anyone else. Also, if you gave someone too much/too little access, you can fix that.

Quick start
-----------
Most users should just be using the [online version](https://sked.tevp.net/)

Local development
-----------------
1. [Install Docker](https://docs.docker.com/engine/installation/) and [Docker Compose](https://docs.docker.com/compose/install/)
2. [Make a new Google OAuth 2 web app](https://support.google.com/cloud/answer/6158849). Javascript origin should be `http://localhost:8000` and Authorised redirect URIs should be `http://localhost:8000/oauth2callback`.
3. [Enable "Google Calendar API" on the developer console](https://support.google.com/cloud/answer/6158841)
4. Copy `.env.example` to `.env`, add your new OAuth secret/ID and run `source .env`
5. Run `docker-compose up --build`
6. Goto [http://localhost:8000](http://localhost:8000)

Docker-less local builds
------------------------
The Docker build is the best option, but here's how to do it without

1. Do steps 2-4 of "Local development" to setup Google auth
2. `python manage.py migrate`
3. `python manage.py createcachetable`
4. `python manage.py runserver 0.0.0.0:8000`
5. Goto [http://localhost:8000](http://localhost:8000)
