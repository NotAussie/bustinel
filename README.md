[![Adelaide Metro bus #1121 taken by NotAussie](https://github.com/user-attachments/assets/093e6940-72eb-40f7-ac73-30b50a46e0bc)](https://github.com/notaussie)

# Bustinel

> ![WARNING]
> Bustinel is undergoing a major rewrite and transition to use the `bubus` framework. Only use the `stable` releases, `latest` and `2.*.*` tags are unstable and may cause.

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

| Variable Name               | Description                                                                             | Default Value                                           | Required |
| --------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------- | -------- |
