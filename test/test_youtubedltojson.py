from Savetube.youtubedltojson import YoutubedlTojson

jsonp = YoutubedlTojson("https://www.youtube.com/watch?v=JycDuXzwwx0")


class Test_youtubedltojson:

    def test_title(self):
        assert jsonp.getTitle() == "The New World order is final. And it is terrible news for PRC"

    def test_thubnail(self):
        assert jsonp.getImgurl() == "https://i.ytimg.com/vi/JycDuXzwwx0/maxresdefault.jpg"

    def test_extractor(self):
        assert jsonp.getExtractor() == "youtube"

    def test_uploader(self):
        assert jsonp.getUploader() == "The Frustrated Indian"
