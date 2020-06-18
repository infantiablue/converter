import unittest
import json
from utils.process import download


class ProcessTestCase(unittest.TestCase):

    def test_download_with_long_video(self):
        # input long video
        result = json.loads(
            download(['https://www.youtube.com/watch?v=XULUBg_ZcAU']))
        assert result['status'] == False

    def test_download_with_live_video(self):
        # input live video
        result = json.loads(
            download(['https://www.youtube.com/watch?v=A31dKWfy0fc']))
        assert result['status'] == False
