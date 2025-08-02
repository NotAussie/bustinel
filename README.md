[![Adelaide Metro bus #1121 taken by NotAussie](https://github.com/user-attachments/assets/093e6940-72eb-40f7-ac73-30b50a46e0bc)](https://github.com/notaussie)



# Bustinel

A tool for generating historical vehicle trip data for analysation and statistical purposes.

## Why create this?

The story that lead to Bustinel's creation is a weird and kinda goofy one. I'm a public transport photographer and enthusiast, my local transit has some pretty cool experimental vehicles and I've had them on my photography bucket list for awhile, annoyingly they aren't in service often and when they are they only service a select few routes, so I thought making an entire framework for generating historical trips would be a fun way to solve this problem. _(Yes I know I could of rang my agency, but what's the fun in that?)_

## Usage

I recommend hosting Bustinel via docker compose, especially if you're using multiple sources _(for example if you wanted to track multiple agencies or multiple agency sources)_. To use it with Docker compose you'll need a `compose.yml` file, we provide an example of what that'll look like inside `example.compose.yml`, I recommend using that as a base.

An example `compose.yml` file would look like this:

```yaml
services:
  analytics:
    image: ghcr.io/notaussie/bustinel:latest
    depends_on:
      - mongo
    environment:
      MONGODB_URL: mongodb://mongo:27017/bustinel
      GOOGLE_TRANSIT_FILE_URL: https://gtfs.adelaidemetro.com.au/v1/static/latest/google_transit.zip
      FEED_URL: https://gtfs.adelaidemetro.com.au/v1/realtime/vehicle_positions
      CONTACT_EMAIL: username@example.com
    restart: always

  mongo:
    image: mongo:latest
    restart: always
    volumes:
      - bustinel-mongo:/data/db

volumes:
  bustinel-mongo:
```

## Environment Variables

Configurable environment variables for Bustinel. Values labelled with required must be set before running the application, if these aren't provided the program will early exit with an error.

| Variable Name               | Description                                                                             | Default Value | Required |
| --------------------------- | --------------------------------------------------------------------------------------- | ------------- | -------- |
| `MONGODB_URL`               | The MongoDB connection URL for the Bustinel database.                                   | N/A           | True     |
| `FEED_URL`                  | The URL to the GTFS‑RT feed for vehicle positions.                                      | N/A           | True     |
| `GOOGLE_TRANSIT_FILE_URL`   | The URL to the Google Transit feed file.                                                | N/A           | True     |
| `FEED_UPDATE_INTERVAL`      | The interval in seconds to update the feed data.                                        | 60            | False    |
| `CONTACT_EMAIL`             | The host's contact email address for complaints or inquiries.                           | N/A           | True     |
| `LOG_LEVEL`                 | The logging level for the application.                                                  | info          | False    |
| `ENVIRONMENT`               | The environment the application is running in (e.g., production, development, testing). | production    | False    |
| `SENTRY_DSN`                | The Sentry DSN for error reporting. (Recommended)                                       | N/A           | False    |
| `SENTRY_TRACES_SAMPLE_RATE` | The sample rate for traces sent to Sentry.                                              | 0.5           | False    |

## HTTP Headers

Enforced HTTP headers for requests made by Bustinel.

| Header Name  | Description                                                             |
| ------------ | ----------------------------------------------------------------------- |
| `User-Agent` | Bustinel <https://github.com/notaussie/bustinel>; contact: _Your email_ |
| `From`       | _Your email_                                                            |
| `Accept`     | application/x-google-protobuf, application/x-protobuf                   |
