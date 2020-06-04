import subprocess
import json


class YoutubedlTojson:

    def __init__(self, videourl):
        shellcmd = "youtube-dl --dump-json {}".format(videourl)
        self.result = subprocess.check_output(shellcmd, shell=True)
        # print(self.result, "")
        self.jsonresult = json.loads(self.result)
        self.formats = self.jsonresult['formats']

    def getImgurl(self):
        try:
            thumb = "{}".format(self.jsonresult['thumbnails'])
            print(thumb.replace("\'", "\""))
            json_data = json.loads(thumb.replace("\'", "\""))
            thumbnail = json_data[0]['url']
            return thumbnail
        except KeyError:
            return "https://webmaster.ypsa.org/wp-content/uploads/2012/08/no_thumb.jpg"

    def getTitle(self):
        return self.jsonresult['title']

    def getExtractor(self):
        return self.jsonresult['extractor']

    def getUploader(self):
        try:
            return self.jsonresult['uploader']
        except KeyError:
            return "None"

    def getDescription(self):
        return self.jsonresult['description']

    def getFormatsExt(self):
        ext = tuple()
        ext = ext + ("mp3",)
        for f in self.formats:
            try:
                if f['ext'] not in ext:
                    ext = ext + (f['ext'],)
            except KeyError:
                return "Available"
        return ext

    def getFormatsHeight(self):
        heights = tuple()
        for h in self.formats:
            try:
                if h['height'] not in heights:
                    heights = heights + (h['height'],)
            except KeyError:
                return "Best"
        return heights
