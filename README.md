# bing_wallpaper

A scripy to download bing daily wallpaper

## Usage

```
usage: app.py [-h] [--storage-dir STORAGE_DIR] [--download-dir DOWNLOAD_DIR] [--download-timeout DOWNLOAD_TIMEOUT] [--filelog] [--log-dir LOG_DIR]
              [--scan-interval SCAN_INTERVAL] [--notify-mail NOTIFY_MAIL] [--my-notify-mail MY_NOTIFY_MAIL] [--my-notify-pass MY_NOTIFY_PASS]
              [--my-notify-name MY_NOTIFY_NAME] [--server-chan-key SERVER_CHAN_KEY]

A tool to download bing daily wallpaper.

options:
  -h, --help            show this help message and exit

General Options:
  --storage-dir STORAGE_DIR
                        directory to store database file, env: BING_STORAGE_DIR (default: storage)
  --download-dir DOWNLOAD_DIR
                        directory to store image file, env: BING_DOWNLOAD_DIR (default: download)
  --download-timeout DOWNLOAD_TIMEOUT
                        download timeout ms, env: BING_DOWNLOAD_TIMEOUT (default: 5000)
  --filelog             write log to file, otherwise to stdout (default: False)
  --log-dir LOG_DIR     directory to store log file if filelog is true, env: BING_LOG_DIR (default: log)
  --scan-interval SCAN_INTERVAL
                        every scan-interval seconds to get bing wallpaper, 0 means run once, env: BING_SCAN_INTERVAL (default: 0)

Notify Options:
  --notify-mail NOTIFY_MAIL
                        email to notify when success or failed download, env: BING_NOTIFY_MAIL (default: None)
  --my-notify-mail MY_NOTIFY_MAIL
                        email to send notify email, env: BING_MY_NOTIFY_MAIL (default: None)
  --my-notify-pass MY_NOTIFY_PASS
                        my-email password or token, env: BING_MY_NOTIFY_PASS (default: None)
  --my-notify-name MY_NOTIFY_NAME
                        user name to send notify email, env: BING_MY_NOTIFY_NAME (default: Robot)
  --server-chan-key SERVER_CHAN_KEY
                        server-chan token to notify, env: BING_SERVER_CHAN_KEY (default: None)

```

All args can be read from environment variables, the environment variables with prefix `BING_`.

## Docker Usage

```shell
docker run -d \
  -e BING_SCAN_INTERVAL=3600 \
  -e BING_NOTIFY_MAIL=example@qq.com \
  -e BING_MY_NOTIFY_MAIL=example@163.com \
  -e BING_MY_NOTIFY_PASS=password \
  -e BING_SERVER_CHAN_KEY=xxx \
  -v /path/to/storage/folder:/bing/storage \
  -v /path/to/download/folder:/bing/download \
  littleneko/bing-dl:latest
```
