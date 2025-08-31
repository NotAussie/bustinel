[![Adelaide Metro bus #1121 taken by NotAussie](https://github.com/user-attachments/assets/093e6940-72eb-40f7-ac73-30b50a46e0bc)](https://github.com/notaussie)

# Bustinel

A lightweight microservice for archiving GTFS-RT trips.

## 💡 Features

- Written in Go, performing ~10x faster than both `v1` and `v2`.
- Forward-compatible-only changes.  

## ❓ Why Create This?

Bustinel came about as a solution to a niche problem of mine, I'm a photographer and public transport enthusiast. And my local agency _(Adelaide Metro)_ has a few experimental vehicles they operate periodically, my goal has been to photograph and ride these buses, annoying due to their inconsistent schedule I had to get creative to track them down... this being the result of getting creative. 

## ✨ Start Tracking

To start tracking agencies you'll need the following;
1. [MongoDB](https://github.com/mongodb/mongo) or [FerretDB](https://github.com/FerretDB/FerretDB) instance.
2. [Redis](https://github.com/redis/redis) or [DragonflyDB](https://github.com/dragonflydb/dragonfly) instance.
3. [Docker](https://github.com/docker) or [Podman](https://mobyproject.org/).

>[!NOTE]
> The example below assumes you're using MongoDB, DragonflyDB, and Podman, you may need to edit parts to reflect your setup.

First we need a network so our services can interact, luckily Podman provides networks for this exact usecase.
```bash
$ podman network create bustinel
```

Before we can spin up our databases we'll need to allow them to store data, we can do this with Podman's `volume` tool.

```bash
$ podman volume create bustinel-mongodb
```

Now we've got a network and volume set up, we can spin up our databases.

```
$ podman run -d \
  --name bustinel-dragonflydb \
  --network bustinel \
  docker.dragonflydb.io/dragonflydb/dragonfly
```

```
$ podman run -d \
  --name bustinel-mongo
  --network bustinel \
  mongo:noble
```

Now finally we can spin up our Bustinel instance, remember to set your feed and metadata urls to their respective counterparts.

```bash
$ podman run -d \
  -e FEED_URL=https://example.com/vehicle-positions \
  -e METADATA_URL=https://example.com/google.zip \
  -e MONGO_URI=mongodb://bustinel-mongo:27017/bustinel \
  -e REDIS_URI=redis://bustinel-dragonflydb:6379/0 \
  -e EMAIL=johndoe@example.com \
  ghcr.io/notaussie/bustinel:stable
```



## 🔑 Environment Variables

Configurable environment variables for Bustinel. Values labelled with required must be set before running the application, if these aren't provided the program will early exit with an error.

| Variable Name | Description | Default Value | Required |
| ------------- | ----------- | ------------- | -------- |