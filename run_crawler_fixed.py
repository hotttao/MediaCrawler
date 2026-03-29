import tempfile
import os

# Override temp directory
tempfile.tempdir = r"D:\Code\media\MediaCrawler\outputs"
os.environ['TEMP'] = tempfile.tempdir
os.environ['TMP'] = tempfile.tempdir

print("Temp dir set to:", tempfile.gettempdir())

# Now run the crawler
os.chdir(r"D:\Code\media\MediaCrawler")
import sys
sys.argv = [
    'main.py',
    '--platform', 'dy',
    '--type', 'creator',
    '--lt', 'qrcode',
    '--get_comment', '0',
    '--save_data_option', 'db'
]

import main
import asyncio
asyncio.get_event_loop().run_until_complete(main.main())