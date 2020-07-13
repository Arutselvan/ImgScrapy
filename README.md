# imgscrapy

![Downloads](https://img.shields.io/pypi/dm/imgscrapy?style=flat-square)

A simple CLI image scraper written in python with support for headless scraping of dynamic websites.

#### Installation
##### Build from source
+ `git clone https://github.com/arutselvan/ImgScrapy`
+ `cd ImgScrapy`
+ `python setup.py install`

##### As a Python package
```
pip install --user imgscrapy
```

#### Requirements
python>=3.6

#### Usage
```
usage: imgscrapy [-h] [-d DIRECTORY] [-i] [-n NFIRST] [-t NTHREADS] [-hd] [-to TIMEOUT] target_url

Downloads images from the given URL

positional arguments:
  target_url            URL to scrape images from
optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory in which images should be downloaded
  -i, --injected        Scrape images from a dynamic website and JS injected images
  -n NFIRST, --nfirst NFIRST
                        Scrape the first n images
  -t NTHREADS, --nthreads NTHREADS
                        Maximum number of threads to use
  -hd, --head           Open chromium for scraping JS injected source/images
  -to TIMEOUT, --timeout TIMEOUT
                        Timeout value for obtaining page source
```
#### Examples

+ Download all images from a static website 
```
imgscrapy <Target URL>
```
+ Download the first 5 images from a dynamic website
```
imgscrapy <Target URL> -i --nfirst 5
```

##### Note
ImgScrapy uses [pyppeteer
](https://github.com/miyakogi/pyppeteer) which uses Chromium for headless scraping. When scraping a dynamic website for the first time, Chromium will be downloaded automatically which might take some time.

#### To Do
+ Write tests
+ Add support for Base64 images
+ Add support for embedded/inline svg files
+ Fix issues with headless browsing of dynamic site with modal/popup
+ Fix issue with missing trailing slash in URL resolution
+ Add option to dump URL of downloaded/failed images

License
----

MIT


