To build docker image use:

```bash
docker build . \
 --tag ghcr.io/notaussie/bustinel:latest \
 --tag ghcr.io/notaussie/bustinel:1.*.*
```

To push the image to GitHub Container Registry, use:

```bash
docker push ghcr.io/notaussie/bustinel:latest && docker push ghcr.io/notaussie/bustinel:1.*.*
```
