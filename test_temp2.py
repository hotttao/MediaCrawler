import os

# Try to directly access the temp directory
temp_path = r"C:\Users\tao\AppData\Local\Temp"
print(f"Testing access to: {temp_path}")
print(f"Exists: {os.path.exists(temp_path)}")
print(f"Is dir: {os.path.isdir(temp_path)}")

# Try to list directory
try:
    files = os.listdir(temp_path)
    print(f"File count: {len(files)}")
except Exception as e:
    print(f"List dir failed: {e}")

# Try to create a file
try:
    test_file = os.path.join(temp_path, "test_qclaw_" + str(os.getpid()))
    with open(test_file, 'w') as f:
        f.write("test")
    print(f"Write test: SUCCESS -> {test_file}")
    os.remove(test_file)
except Exception as e:
    print(f"Write test FAILED: {e}")