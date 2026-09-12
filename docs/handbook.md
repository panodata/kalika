# Handbook

## Install

We recommend using [uv] to install or run `kalika`. [^1][^2]

[^1]: You can install `uv` using `pip install uv`, or another method that matches your operating system.
[^2]: While installing `kalika` with vanilla `pip` is possible, it is an order of magnitude slower.

```bash
pip install uv
uvx kalika
```

Alternatively, if you like to install it account-wide on your system:
```shell
uv tool install kalika
```

## Configure

Multiple or large instances of Heritrix processing many jobs require to
increase certain system limits. Please define in `/etc/sysctl.d/60-local.conf`:
```ini
fs.inotify.max_user_instances = 10240
fs.inotify.max_user_watches = 20037690
```

Then, activate the new settings.
```shell
sysctl --system
```

## Operate

Run Heritrix.
```shell
docker run --detach --init --user root \
    --name heritrix-1 --rm --publish 8443:8443 \
    --env "USERNAME=admin" --env "PASSWORD=admin" --env "JAVA_OPTS=-Xmx4096M" \
    --volume /var/heritrix-1:/opt/heritrix/jobs docker.io/iipc/heritrix
```

Feed a list of URLs.
```shell
tmux new -s feed
export HERITRIX_URL="https://heritrix.example.org:8443/engine"
kalika add feed.txt
```

Drain WARC files into target directory.
```shell
tmux new -s drain
export HERITRIX_URL="https://heritrix.example.org:8443/engine"
kalika drain /media/archive
```


[uv]: https://github.com/astral-sh/uv
