# bing_wallpaper

A scripy to download bing daily wallpaper

## Usage

```
usage: app.py [-h] [--server-mode] [--scan-interval SCAN_INTERVAL] [--log-type {stdout,file}] [--log-path LOG_PATH] [--log-level {DEBUG,INFO,WARNING,ERROR}]
              [--storage-type {NONE,SQLITE}] [--storage-path STORAGE_PATH] [--download-path DOWNLOAD_PATH] [--download-timeout DOWNLOAD_TIMEOUT] [--retries RETRIES]
              [--zone {CN,EN}] [--count {1,2,3,4,5,6,7,8}] [--notify-mail NOTIFY_MAIL] [--notify-user-mail NOTIFY_USER_MAIL] [--notify-user-pass NOTIFY_USER_PASS]
              [--notify-user-name NOTIFY_USER_NAME] [--server-chan-key SERVER_CHAN_KEY]

A tool to download bing daily wallpaper.

options:
  -h, --help            show this help message and exit

General Options:
  --server-mode         run as server and scan new wallpaper cyclically, otherwise only run once (default: False)
  --scan-interval SCAN_INTERVAL
                        seconds to check new wallpaper if run in server mode, env: BING_SCAN_INTERVAL (default: 3600)
  --log-type {stdout,file}
                        write log to file or stdout, env: BING_LOG_TYPE (default: stdout)
  --log-path LOG_PATH   location for log file if filelog is true, env: BING_LOG_PATH (default: log)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        location for log file if filelog is true, env: BING_LOG_LEVEL (default: INFO)
  --storage-type {NONE,SQLITE}
                        how to store wall paper info and check wallpaper exist, NONE for no check, env: BING_STORAGE_TYPE (default: SQLITE)
  --storage-path STORAGE_PATH
                        location for sqlite database files, env: BING_STORAGE_PATH (default: storage)
  --download-path DOWNLOAD_PATH
                        location for downloaded image files, env: BING_DOWNLOAD_PATH (default: download)
  --download-timeout DOWNLOAD_TIMEOUT
                        download timeout millisecond, env: BING_DOWNLOAD_TIMEOUT (default: 5000)
  --retries RETRIES     times to retry when failed to download, env: BING_RETRIES (default: 3)

Bing Options:
  --zone {CN,EN}        where to download wallpaper, env: BING_ZONE (default: CN)
  --count {1,2,3,4,5,6,7,8}
                        how many wallpaper to download, env: BING_COUNT (default: 8)

Notify Options:
  --notify-mail NOTIFY_MAIL
                        send email to this address after download, env: BING_NOTIFY_MAIL (default: None)
  --notify-user-mail NOTIFY_USER_MAIL
                        email to send notify email, env: BING_NOTIFY_USER_MAIL (default: None)
  --notify-user-pass NOTIFY_USER_PASS
                        notify user email password or token, env: BING_NOTIFY_USER_PASS (default: None)
  --notify-user-name NOTIFY_USER_NAME
                        notify user name to send email, env: BING_NOTIFY_USER_NAME (default: Robot)
  --server-chan-key SERVER_CHAN_KEY
                        server-chan token to notify, env: BING_SERVER_CHAN_KEY (default: None)

```

All args can be read from environment variables, the environment variables with prefix `BING_`.

## Docker Usage

```shell
docker run -d \
  -e BING_SCAN_INTERVAL=3600 \
  -e BING_NOTIFY_MAIL=example@qq.com \
  -e BING_NOTIFY_USER_MAIL=example@163.com \
  -e BING_NOTIFY_USER_PASS=password \
  -e BING_SERVER_CHAN_KEY=xxx \
  -v /path/to/storage/folder:/bing/storage \
  -v /path/to/download/folder:/bing/download \
  littleneko/bing-dl:latest
```
