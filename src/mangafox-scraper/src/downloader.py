class Downloader:
    def __init__(self):
        pass

    def download_content(self, content, filename):
        self.save_to_file(content, filename)

    def save_to_file(self, content, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)