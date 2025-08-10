import os

def is_docker():
    path = '/proc/self/cgroup'
    res = False
    if os.path.isfile(path):
        with open(path, 'r') as f:
            res = any('docker' in line for line in f)
    return os.path.exists('/.dockerenv') or res