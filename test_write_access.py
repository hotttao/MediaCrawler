import os

# Test different directories for write access
dirs_to_test = [
    r"D:\Code\media\MediaCrawler",
    r"D:\Code\media\MediaCrawler\outputs",
    r"D:\Code\media\MediaCrawler\cache",
    r"D:\Code\media\MediaCrawler\browser_data",
    r"C:\Users\tao\.qclaw",
    r"C:\Users\tao",
]

for d in dirs_to_test:
    if os.path.exists(d):
        try:
            test_file = os.path.join(d, "test_write_" + str(os.getpid()))
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"✓ {d}")
        except Exception as e:
            print(f"✗ {d}: {e}")
    else:
        print(f"? {d}: does not exist")