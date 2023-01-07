# bing_wallpaper

A scripy to download bing daily wallpaper

## Usage

```
usage: app.py [-h] [--service-mode] [--scan-interval SCAN_INTERVAL] [--log-type {stdout,file}] [--log-path LOG_PATH] [--log-level {DEBUG,INFO,WARNING,ERROR}]
              [--storage-type {NONE,SQLITE}] [--storage-path STORAGE_PATH] [--download-path DOWNLOAD_PATH] [--download-timeout DOWNLOAD_TIMEOUT] [--retries RETRIES]
              [--search-zone {CN,EN}] [--day-offset {0,1,2,3,4,5,6,7}] [--day-count {1,2,3,4,5,6,7,8}] [--notify-mail NOTIFY_MAIL] [--notify-user-mail NOTIFY_USER_MAIL]
              [--notify-user-pass NOTIFY_USER_PASS] [--notify-user-name NOTIFY_USER_NAME] [--server-chan-key SERVER_CHAN_KEY]

A tool to download bing daily wallpaper.

options:
  -h, --help            show this help message and exit

General Options:
  --service-mode        Run as service and periodically scan new wallpaper, otherwise only run once (default: False)
  --scan-interval SCAN_INTERVAL
                        Check new wallpaper every scan-interval millisecond if run in server mode, env: BING_SCAN_INTERVAL (default: 3600)
  --log-type {stdout,file}
                        Write log to file or stdout, env: BING_LOG_TYPE (default: stdout)
  --log-path LOG_PATH   Location for log file if log-type is file, env: BING_LOG_PATH (default: log)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level, env: BING_LOG_LEVEL (default: INFO)
  --storage-type {NONE,SQLITE}
                        The way to store wallpaper info and check exist, NONE means not store and not check, env: BING_STORAGE_TYPE (default: SQLITE)
  --storage-path STORAGE_PATH
                        Location for database files if storage-type is not NONE, env: BING_STORAGE_PATH (default: storage)
  --download-path DOWNLOAD_PATH
                        Location for downloaded wallpaper files, env: BING_DOWNLOAD_PATH (default: download)
  --download-timeout DOWNLOAD_TIMEOUT
                        Download timeout millisecond, env: BING_DOWNLOAD_TIMEOUT (default: 5000)
  --retries RETRIES     Times to retry when failed to download, env: BING_RETRIES (default: 3)

Bing Options:
  --search-zone {CN,EN}
                        Search in bing china or international web site, env: BING_SEARCH_ZONE (default: CN)
  --day-offset {0,1,2,3,4,5,6,7}
                        The num days before today start to get, env: BING_DAY_OFFSET (default: 0)
  --day-count {1,2,3,4,5,6,7,8}
                        The bing API can get up to 8 days of wallpaper before today, env: BING_DAY_COUNT (default: 8)

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

Run as service and periodically scan new wallpaper:

```shell
docker run -d \
  -e BING_SCAN_INTERVAL=3600 \
  -e BING_NOTIFY_MAIL=example@qq.com \
  -e BING_NOTIFY_USER_MAIL=example@163.com \
  -e BING_NOTIFY_USER_PASS=password \
  -v /path/to/storage/folder:/bing/storage \
  -v /path/to/download/folder:/bing/download \
  littleneko/bing-dl:latest
```
