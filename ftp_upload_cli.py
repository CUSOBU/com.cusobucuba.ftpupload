import os
import re

import fire
import git
from fs import open_fs
from fs.wrap import read_only, cache_directory

repo_url = 'https://github.com/covid19cuba/covid19cubadata.github.io.git'
root = 'covid19cubadataactions'
upload_root = '/api'
ftp_dir = '/htdocs/covid/'
ftp_command = 'lftp -u {user},{password} -p {port} -e "set ssl:verify-certificate false;{command}exit;" {host}'
mkdir_str = 'cd ' + ftp_dir + '{folder}' + ' || mkdir -p ' + ftp_dir + '{folder}' + ';cd ' + ftp_dir + '{folder}' + ';'
branch = 'gh-pages'


class LeaveMissing(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def get_last_commit():
    r = git.Repo.init('temp_repo')
    r.create_remote('origin', repo_url)
    res = str(r.git.ls_remote(repo_url)).replace('\t', ' ')
    r.close()
    os.system('rm -rf temp_repo')
    regex = '(?P<commit>[a-z0-9]+) ' + re.escape("refs/heads/" + branch)
    matchObj = re.search(regex, res)
    if matchObj:
        return matchObj.group('commit')
    return None


def mkdir(folder):
    return mkdir_str.format(folder=folder)


def walk_upload(root, folder):
    if not os.path.isdir(root) and not os.path.isdir(folder):
        return

    with read_only(cache_directory(open_fs(root))) as home_fs:

        for dir_path in home_fs.walk.dirs(folder):
            print("Processing", dir_path)
            entry = root + dir_path
            os.system(ftp_command.format(command=mkdir(dir_path) + 'mput -P 2 ' + entry + '/*;'))
            print("Uploaded", dir_path)


def run_update(host, user, password, port=21):
    global ftp_command
    ftp_command = ftp_command.format_map(LeaveMissing(user=user, password=password, host=host, port=port))

    last_commit = None
    if os.path.isfile('last_commit'):
        with open('last_commit', 'r') as file:
            last_commit = file.readline().strip()

    remote_commit = get_last_commit()
    if remote_commit == last_commit:
        print('Already up to date')
    else:
        os.system('git clone -b {0} --depth=1 {1} {2}'.format(branch, repo_url, root))
        print('Will need to update', remote_commit, last_commit)
        walk_upload(root, upload_root)

        with open('last_commit', 'w') as file:
            file.write(remote_commit)

    os.system('rm -rf ' + root)


if __name__ == "__main__":
    fire.Fire(run_update)
