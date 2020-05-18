class PageLoadError(Exception):
    """
    Exception to be raised when there is a error in loading the page
    """

    def __init__(self, status_code=0):
        super(PageLoadError, self).__init__()
        self.status_code = status_code


class FileCreateError(Exception):
    """
    Exception to be raised when the file cannot be created
    """

    pass


class DirectoryCreateError(Exception):
    """
    Exception to be raised when new directory cannot be created
    """

    pass


class DownloadError(Exception):
    """
    Exception to be raised when the image cannot be downloaded.
    """

    status_code = 0

    def __init__(self, status_code=0):
        super(DownloadError, self).__init__()
        self.status_code = status_code
