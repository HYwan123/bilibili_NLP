import subprocess

cmd = [
    "curl",
    "https://api.aicu.cc/api/v3/search/getreply?uid=66143532&ps=100&pn=1&mode=0&keyword="
]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)