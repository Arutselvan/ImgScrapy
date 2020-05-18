from imgscrapy.utils import Utilities
from imgscrapy.utils import ImgScrapy
from pyfiglet import Figlet
from clint.textui import puts, colored, indent

def main():

    try:
        f = Figlet(font='slant', width=80)
        puts(colored.cyan(f.renderText('imgscrapy')));
        args = Utilities.parse_args_and_flags()
        scraper = ImgScrapy(*args)
        scraper.scrape_images()

    except KeyboardInterrupt:
        puts(colored.red("\nimgscrapy has been stopped by user"))
