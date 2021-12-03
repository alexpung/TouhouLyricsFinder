class ContentNotFoundError(Exception):
    def __init__(self, url, status_code):
        self.url = url
        self.status_code = status_code

    def __str__(self):
        return f"URL {self.url} return with status code {self.status_code}"
