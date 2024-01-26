# Aus GLAMR

A django app running on Docker. Replaces _Aus GLAM Blogs_.

## Deploy

* `docker compose build`
* `./glamr-dev makemigrations` (may get a DB connection error here, ignore it or run again)
* `./glamr-dev migrate`
* `./glamr-dev createsuperuser`
* `docker compose up`
* set up database backups (as cron jobs): `./glamr-dev backup`:
* set up cron jobs for management commands as below

## Admin

Don't forget to add some Content Warnings for use by the Mastodon bot, within `/admin`.

## CLI tool

Use `glamr-dev` to make your life easier (thanks to Mouse Reeve for the inspiration):

* announce
* backup
* check_feeds
* manage [django management command]
* makemigrations
* migrate
* queue_announcements
* send_weekly_email

And for dev work:

* black
* collectstatic
* createsuperuser
* pylint
* resetdb
* test

## Registration

- users can register a blog, group, event, newsletter, or Call for Papers.
- most of these ask for an "owner email" - this is optional but allows us to communicate with the person registering.
- all registrations should trigger an email to admin
- all must be approved before they are included

## Management commands

There are four commands:

- announce
- check_feeds
- queue_announcements
- send_weekly_email

These will not be triggered within the app - they should be called via cron jobs.

### announce

This announces the next queued announcement on Mastodon.

Run every 21 mins.

### check_feeds

This checks all blog feeds for any new posts, and adds them to the database as long as they don't have an exclusion tag and were not published during a time the blog was suspended.

Also checks newsletter articles if there is a feed.

Run every hour.

### queue_announcements

This queues announcements for events and CFPs. These are announced three times, evenly spaced between when they were added and when the event starts or the CFP closes.

Run daily.

### send_weekly_email

Does what you think. Creates a weekly email of the latest stuff, and send to everyone in Subscribers.

Run weekly.

### Backups

There is a `backup` command in `glamr-dev`. You can adjust the filepaths in your `.env` file.

Run daily