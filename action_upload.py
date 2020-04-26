import os
import json
import requests
from fs import open_fs
from fs.path import join
from fs.wrap import read_only, cache_directory
try:
    import dotenv
    dotenv.load_dotenv('.env')
except Exception:
    pass
token = os.environ.get('TOKEN')

user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'
#url = 'https://www.cusobu.nat.cu/testing/index.php'
url = 'http://127.0.0.1/test/index.php'


ss=requests.Session()
ss.headers['User-Agent']=user_agent
ss.headers['TOKEN']=token

def walk_upload(folder):
    if not os.path.isdir(folder):
        return

    with read_only(cache_directory(open_fs('.'))) as home_fs:
        for walker in home_fs.walk(folder):
            path = walker.path
            ss.headers['JSON-PATH']=path
            for file in walker.files:
                name = file.name
                ss.headers['JSON-NAME']=name
                with home_fs.open(join(path,name)) as f:
                    data = f.read()
                ss.post(url, data=data)

def upload():
    data_hash = json.load(open('api/v1/state.json'))['data']
    ss.headers['DATA-HASH']=data_hash
    r = ss.post(url)
    print(r.content)
    if r.json()['update']:
        walk_upload('api')

