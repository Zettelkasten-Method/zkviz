from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from zkviz import zkviz


class TestListZettels(TestCase):

    def test_list_zettels_with_md_extension(self):
        # Create a temporary folder and write files in it
        with TemporaryDirectory() as tmpdirname:
            ext = '.md'
            basename = '201906242157'
            filepaths = []
            for i in range(3):
                path = Path(tmpdirname, basename + str(i) + ext)
                path.touch()
                filepaths.append(str(path))

            files_found = zkviz.list_zettels(tmpdirname)
            self.assertEqual(filepaths, files_found)

    def test_list_zettels_with_txt_extension(self):
        # Create a temporary folder and write files in it
        with TemporaryDirectory() as tmpdirname:
            ext = '.txt'
            basename = '201906242157'
            filepaths = []
            for i in range(3):
                path = Path(tmpdirname, basename + str(i) + ext)
                path.touch()
                filepaths.append(str(path))

            files_found = zkviz.list_zettels(tmpdirname, '*.txt')
            self.assertEqual(filepaths, files_found)

    def test_list_zettels_with_mixed_extensions(self):
        # Create a temporary folder and write files in it
        with TemporaryDirectory() as tmpdirname:
            filepaths = []
            basename = '201906242157'

            ext = '.txt'
            for i in range(5):
                path = Path(tmpdirname, basename + str(i) + ext)
                path.touch()
                filepaths.append(str(path))

            ext = '.md'
            for i in range(5, 10):
                path = Path(tmpdirname, basename + str(i) + ext)
                path.touch()
                filepaths.append(str(path))

            files_found = zkviz.list_zettels(tmpdirname, '*.txt|*.md')
            self.assertEqual(filepaths, files_found)


class TestParseArgs(TestCase):

    def test_default_extension(self):
        args = zkviz.parse_args('')
        self.assertEqual(['*.md'], args.pattern)

    def test_overwrite_extension(self):
        args = zkviz.parse_args(["--pattern","*.txt"])
        self.assertEqual(['*.txt'], args.pattern)

    def test_multiple_extensions(self):
        args = zkviz.parse_args(["--pattern","*.txt", "--pattern", '*.md'])
        self.assertEqual(['*.txt', '*.md'], args.pattern)
