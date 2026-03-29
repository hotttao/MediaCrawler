import tempfile
import os

print("TEMP:", os.environ.get('TEMP'))
print("TMP:", os.environ.get('TMP'))
print("TMPDIR:", os.environ.get('TMPDIR'))
print("gettempdir():", tempfile.gettempdir())

# Try to create a temp file
try:
    fd, path = tempfile.mkstemp()
    print("mkstemp succeeded:", path)
    os.close(fd)
    os.remove(path)
except Exception as e:
    print("mkstemp failed:", e)