# bing_wallpaper
a scripy to download bing daliy wallpaper

## Docker Usage

```shell
docker run \
  -v /path/to/your/config:/bing/config \
  -v /path/to/your/database:/bing/database \
  -v /path/to/your/wallpaper:/bing/wallpaper \
  bing-dl:latest
```