"""
Wrapper script to set temp directory before running the crawler
"""
import os
import sys
import tempfile

# Override temp directory to use a writable location
tempfile.tempdir = r"D:\Code\media\MediaCrawler\cache\temp"
os.makedirs(tempfile.tempdir, exist_ok=True)

# Also set environment variables
os.environ['TEMP'] = tempfile.tempdir
os.environ['TMP'] = tempfile.tempdir
os.environ['TMPDIR'] = tempfile.tempdir

# Now import and run the main script
sys.argv = [
    'main.py',
    '--platform', 'dy',
    '--type', 'creator',
    '--lt', 'qrcode',
    '--get_comment', '0',
    '--save_data_option', 'db'
]

import main
main.main()
