from threading import Thread
import sys
from urllib.parse import urljoin
from lxml import html
import os
from imgscrapy.exceptions import PageLoadError, DownloadError, FileCreateError, DirectoryCreateError
from re import match
import argparse
import requests
from progressbar import ProgressBar
from clint.textui import puts, colored, indent

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from Queue import Queue
else:
    from queue import Queue


class Utilities:
    """
    Collection of Utilities
    """

    @staticmethod
    def parse_args_and_flags():
        """ 
        Gets the arguments from the command line. 
        """

        parser = argparse.ArgumentParser(
            description='Downloads images from the given URL')
        parser.add_argument('target_url', nargs=1,
                            help="URL to scrape images from")
        parser.add_argument('-d', '--directory', type=str, default="imgscrapy-images",
                            help="Directory in which images should be downloaded")
        parser.add_argument('-ds', '--dynamic-site', action='store_true',
                            help="Scrape images from a dynamic website and JS injected images")

        args = parser.parse_args()

        url = args.target_url[0]

        if not match(r'^[a-zA-Z]+://', url):
            url = 'http://' + url

        return url, args.directory, args.dynamic_site


class Worker(Thread):
    """
    Thread executing tasks from a given tasks queue
    """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except:
                # An exception happened in this thread
                pass
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """
    Pool of threads consuming tasks from a queue
    """

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """
        Add a task to the queue
        """

        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """
        Add a list of tasks to the queue
        """

        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """
        Wait for completion of all the tasks in the queue
        """

        self.tasks.join()


class ImgScrapy:
    """
    Image scraper class
    """

    def __init__(self, page_url, directory, dynamic_site):
        self.page_url = page_url
        self.dom = None
        self.img_links = []
        self.img_count = 0
        self.downloaded_links = []
        self.failed_links = []
        self.directory = directory
        self.download_directory = os.path.join(
            directory, page_url.split('/')[2])
        self.processed_count = 0
        self.is_dynamic_site = dynamic_site
        self.max_threads = 10
        self.ds_timeout = 0

    def gethtmlsource(self, page_url):
        """
        Method to get HTML source
        """
        dom = None
        try:
            page_request = requests.get(page_url)

            if page_request.status_code == 200:
                dom = html.fromstring(page_request.text)
            else:
                raise PageLoadError(page_request.status_code)
        except:
            raise PageLoadError()

        return dom

    async def getdynamichtmlsource(self, page_url):
        """
        Method to get HTML  source
        """
        from pyppeteer import launch, dialog , errors as pypperrors
        browser = await launch(headless=True)
        page = await browser.newPage()
        try:
            await page.goto(page_url)
            content = await page.evaluate('document.body.outerHTML')
            await browser.close()
            return html.fromstring(content)
        except pypperrors.TimeoutError:
            print("Page Loading timed out. If it's a heavy page, increase timeout value. if it has any modal/popup try running with headless set to false")
            raise PageLoadError()
        except:
            raise PageLoadError()

    def acquire_links(self, dom, page_url):
        """
        Method to get images' download links
        """
        img_paths = dom.xpath('//img/@src')
        img_links = []
        for path in img_paths:
            img_link = urljoin(page_url, path)
            if img_link not in img_links:
                img_links.append(img_link)
        return img_links

    def download_img(self, image_link, file_location, pb):
        """
        Method to download an image
        """

        if '?' in file_location:
            file_location = file_location.split('?')[-2]
            
        try:
            image_request = requests.get(image_link, stream=True)
            if image_request.status_code == 200:
                with open(file_location, 'wb') as f:
                    f.write(image_request.content)
                self.downloaded_links.append(image_link)
                self.processed_count+=1
                pb.update(self.processed_count)
            else:
                self.failed_links.append(image_link)
                self.processed_count+=1
                pb.update(self.processed_count)
        except:
            self.failed_links.append(image_link)
            self.processed_count+=1
            pb.update(self.processed_count)
            raise DownloadError()

    def scrape_images(self):
        """
        Method to download images found in the page
        """

        if not os.path.exists(self.download_directory):
            try:
                os.makedirs(self.download_directory)
            except:
                raise DirectoryCreateError()

        with indent(4, quote='>>>'):
            puts(colored.cyan('Getting html page source from ') + colored.yellow(str(self.page_url)))  

        if self.is_dynamic_site:
            import asyncio
            self.dom = asyncio.get_event_loop().run_until_complete(self.getdynamichtmlsource(self.page_url))
        else:
            self.dom = self.gethtmlsource(self.page_url)

        with indent(4, quote='>>>'):
            puts(colored.cyan("Processing html"))

        self.img_links = self.acquire_links(self.dom, self.page_url)
        self.img_count = len(self.img_links)

        with indent(4, quote='>>>'):
            puts(colored.cyan("Found") + " " +  colored.yellow(str(self.img_count) + " " + colored.cyan("images")))
            puts(colored.cyan("Downloading images to " + self.download_directory))

        pool_size = max(self.img_count, self.max_threads)
        pool = ThreadPool(pool_size)

        pb = ProgressBar(maxval=self.img_count).start()

        for link in self.img_links:
            file_location = self.download_directory+"/" + \
                link.split('/')[len(link.split('/'))-1]
            pool.add_task(self.download_img, link, file_location,pb)

        pool.wait_completion()
        pb.finish()

        puts(colored.green("\nSuccessfull downloads: " + str(len(self.downloaded_links))))
        puts(colored.red("Failed downloads: " + str(len(self.failed_links))))