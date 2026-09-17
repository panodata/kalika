(handbook)=

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

### Crawl

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
kalika heritrix add feed.txt
```

Drain WARC files into target directory.
```shell
tmux new -s drain
export HERITRIX_URL="https://heritrix.example.org:8443/engine"
kalika heritrix drain /media/archive
```

### Replay

```shell
mkdir /media/replay
cd /media/replay
wb-manager init research-1
wb-manager add research-1 /media/archive/www.example.org.warc.gz
kalika serve --directory /media/replay
```

## Tools

Display missing sites by comparing list of input URLs
against files in the WARC output directory.
```shell
kalika urllist compare --url-list urls.txt --directory /media/archive
```

Create equal-sized chunks from URL file, named `urls-00.txt`, `urls-01.txt`,
`urls-02.txt`, etc.
```shell
kalika urllist chunk urls.txt --chunk-size 500
```


[uv]: https://github.com/astral-sh/uv
