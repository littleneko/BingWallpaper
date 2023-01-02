# bing_wallpaper
A scripy to download bing daliy wallpaper

## Docker Usage

```shell
docker run -d \
  -v /path/to/config/folder:/bing/config \
  -v /path/to/database/folder:/bing/database \
  -v /path/to/download/folder:/bing/wallpaper \
  littleneko/bing-dl:latest
```
