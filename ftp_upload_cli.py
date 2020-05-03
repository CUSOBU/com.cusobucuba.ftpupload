import os
import re

import fire
import git
from fs import open_fs
from fs.wrap import read_only, cache_directory

DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + '/'

root = DIRECTORY + 'covid19cubadataactions'
ftp_command = 'lftp -u {user},{password} -p {port} -e "set ssl:verify-certificate false;{command}exit;" {host}'


class LeaveMissing(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def get_last_commit(repo_url, branch):
    temp_repo = DIRECTORY + 'temp_repo'
    if os.path.exists(temp_repo):
        os.system('rm -rf ' + temp_repo)
    r = git.Repo.init(temp_repo)
    r.create_remote('origin', repo_url)
    res = str(r.git.ls_remote(repo_url)).replace('\t', ' ')
    r.close()
    os.system('rm -rf ' + temp_repo)
    regex = '(?P<commit>[a-z0-9]+) ' + re.escape("refs/heads/" + branch)
    match_obj = re.search(regex, res)
    if match_obj:
        return match_obj.group('commit')
    return None


def mkdir(ftp_dir, folder):
    return str('cd ' + ftp_dir + '{folder}' + ' || mkdir -p ' + ftp_dir + '{folder}' + ';cd ' + ftp_dir + '{folder}' + ';').format(folder=folder)


def walk_upload(ftp_dir, root_folder, sub_folder):
    if not os.path.isdir(root_folder) and not os.path.isdir(sub_folder):
        return

    os.system(ftp_command.format(command='cd ' + ftp_dir + sub_folder + ';mput -P 2 ' + root_folder + '/*;'))

    with read_only(cache_directory(open_fs(root_folder))) as home_fs:
        for dir_path in home_fs.walk.dirs(sub_folder, exclude_dirs=["*.git", ".github"]):
            print("Processing", dir_path)
            entry = root_folder + dir_path
            os.system(ftp_command.format(command=mkdir(ftp_dir, dir_path) + 'mput -P 2 ' + entry + '/*;'))
            print("Uploaded", dir_path)


def update_branch(branch, ftp_dir, upload_root, repo_url):
    last_commit_file = DIRECTORY + 'last_commit_' + branch
    last_commit = None
    if os.path.isfile(last_commit_file):
        with open(last_commit_file, 'r') as file:
            last_commit = file.readline().strip()

    remote_commit = get_last_commit(repo_url, branch)
    if remote_commit == last_commit:
        print('Already up to date')
    else:
        os.system('git clone -b {0} --depth=1 {1} {2}'.format(branch, repo_url, root))
        print('Will need to update', remote_commit, last_commit)
        walk_upload(ftp_dir, root, upload_root)

        with open(last_commit_file, 'w') as file:
            file.write(remote_commit)

    os.system('rm -rf ' + root)


def run_update(host, user, password, port=21, ftp_dir='/htdocs/testing'):
    global ftp_command
    ftp_command = ftp_command.format_map(LeaveMissing(user=user, password=password, host=host, port=port))

    update_branch('master', ftp_dir, '/', 'https://github.com/covid19cubadata/covid19cubadata.github.io.git')
    update_branch('gh-pages', ftp_dir, '/api', 'https://github.com/covid19cuba/covid19cubadata.github.io.git')


if __name__ == "__main__":
    fire.Fire(run_update)
