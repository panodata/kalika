# Sandbox

Acquire sources and install package in development mode.
```shell
git clone https://github.com/panodata/kalika
cd kalika
uv venv --python 3.14 --seed .venv
uv pip install --upgrade --editable='.[full,develop,test]'
```

Run linters and software tests.
```shell
poe check
```
