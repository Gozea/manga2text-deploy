# Deployement for Manga2Text

Deployement for serverless apps detailed in the [MangaBubbles](https://github.com/Gozea/MangaBubble) repository

This contains a dockerfile you can use to deploy it on your own server.
=======
## Enable Docker with systemd

```systemctl start docker```

## Docker build

```docker build -t your-name/repo-name:build-version .```

## Docker run

```docker run local-name/local-repo-name:build-version```

## Link local image to remote repo

```docker tag local-name/local-repo-name:build-version remote-account/remote-repo:build-version```

## Push to docker hub

```docker push your-name/repo-name:build-version```

## Remove local containers and images

```docker rm -vf $(docker ps -a -q) && docker rmi -f $(docker images -a -q)```
