import os
import time

import fire
import git

root = 'covid19cubadataactions'
upload_root = root + '/api'
entries = []
ftp_dir = '/htdocs/covid/'
start_ftp = 'lftp -u {user},{password} -e "set ssl:verify-certificate false;'
end_ftp = 'exit;" {host}'


def mkdir(folder):
    return 'cd ' + ftp_dir + folder + ' || mkdir -p ' + ftp_dir + folder + ';cd ' + ftp_dir + folder + ';'


def walk_upload(folder, pause=False):
    if pause:
        time.sleep(1)
    items = os.listdir(folder)
    for i in range(0, len(items)):
        entry = folder + '/' + items[i]
        if os.path.isdir(entry):
            entries.append(folder + '/' + items[i])

    while len(entries):
        entry = entries.pop()
        print("Adding", str(entry).replace('covid19cubadataactions/', ''))
        command = start_ftp + mkdir(str(entry).replace('covid19cubadataactions/', '')) + 'mput -P 2 ' + entry + '/*;' + end_ftp
        os.system(command)
        print("Uploaded", str(entry).replace('covid19cubadataactions/', ''))
        if os.path.isdir(entry):
            walk_upload(entry, True)


def run_update(host, user, password):
    global start_ftp
    start_ftp = start_ftp.format(user=user, password=password, host=host)

    last_commit = None
    if os.path.isfile('last_commit'):
        with open('last_commit', 'r') as file:
            last_commit = file.read().replace('\n', '')

    os.system('git clone -b gh-pages --depth=1 https://github.com/covid19cuba/covid19cubadata.github.io.git ' + root)

    repo = git.Repo(root)
    if str(repo.commit()) == last_commit:
        print('Already up to date')
    else:
        print('Will need to update', repo.commit(), last_commit)
        walk_upload(upload_root)

        with open('last_commit', 'w') as file:
            file.write(str(repo.commit()))

    os.system('rm -rf ' + root)


if __name__ == "__main__":
    fire.Fire(run_update)
