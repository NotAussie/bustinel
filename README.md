[![Adelaide Metro bus #1121 taken by NotAussie](https://github.com/user-attachments/assets/093e6940-72eb-40f7-ac73-30b50a46e0bc)](https://github.com/notaussie)

# Bustinel

A lightweight microservice for archiving GTFS-RT trips.

## 💡 Features

- Written in Go, performing ~10x faster than both `v1` and `v2`.
- Forward-compatible-only changes.

## ❓ Why Create This?

Bustinel came about as a solution to a niche problem of mine, I'm a photographer and public transport enthusiast. And my local agency _(Adelaide Metro)_ has a few experimental vehicles they operate periodically, my goal has been to photograph and ride these buses, annoying due to their inconsistent schedule I had to get creative to track them down... this being the result of getting creative.

## ✨ Start Tracking

To start tracking first you'll need either a [Docker](https://docs.docker.com/) or [Podman](https://podman.io/) installation and either [MongoDB](https://www.mongodb.com/) or [FerretDB](https://ferretdb.com/).

### 🐋 Docker Compose

The compose file below features a [FerretDB](https://ferretdb.com/) instance and Bustinel _(v3)_ instance in a production ready state.

```yml
services:
  postgres:
    image: ghcr.io/ferretdb/postgres-documentdb:17-0.106.0-ferretdb-2.5.0
    restart: on-failure
    environment:
      - POSTGRES_USER=bustinel
      - POSTGRES_PASSWORD=atotallysecurepassword
      - POSTGRES_DB=postgres
    volumes:
      - ./data:/var/lib/postgresql/data

  ferretdb:
    image: ghcr.io/ferretdb/ferretdb:2.5.0
    restart: on-failure
    environment:
      - FERRETDB_POSTGRESQL_URL=postgres://bustinel:atotallysecurepassword@postgres:5432/postgres

  bustinel:
    image: ghcr.io/notaussie/bustinel:stable
    environment:
      - FEED_URL=https://example.com/vehicle-positions
      - METADATA_URL=https://example.com/google.zip
      - MONGO_URI=mongodb://ferretdb:27017/bustinel
      - EMAIL=johndoe@example.com

networks:
  default:
    driver: bridge
```

## 🔑 Environment Variables

Configurable environment variables for Bustinel. Values labelled as required must be set or else the program will exit with a fatal error.

| Variable Name               | Description                                                      | Default Value | Required |
| --------------------------- | ---------------------------------------------------------------- | ------------- | -------- |
| `MONGO_URI`                 | The connection string for your MongoDB instance                  | `nil`         | ✅       |
| `FEED_URL`                  | The URL of the GTFS-RT feed                                      | `nil`         | ✅       |
| `FEED_REFRESH_INTERVAL`     | The interval at which to refresh the GTFS-RT feed in CRON format | `0 * * * *`   | ❌       |
| `METADATA_URL`              | The URL of the GTFS metadata file                                | `nil`         | ✅       |
| `METADATA_REFRESH_INTERVAL` | The interval at which to refresh the metadata in CRON format     | `*/1 * * * *` | ❌       |
| `CONTACT`                   | The host email address to provide when making requests.          | `nil`         | ✅       |

## 🏆 Contributors

<!-- readme: collaborators,contributors -start -->
<!-- readme: collaborators,contributors -end -->
