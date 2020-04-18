import os

import fire
import git

root = 'covid19cubadataactions'
upload_root = root + '/api'
entries = []
ftp_dir = '/htdocs/covid/'
ftp_command = 'lftp -u {user},{password} -e "set ssl:verify-certificate false;{command}exit;" {host}'


class LeaveMissing(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def mkdir(folder):
    return 'cd ' + ftp_dir + folder + ' || mkdir -p ' + ftp_dir + folder + ';cd ' + ftp_dir + folder + ';'


def walk_upload(folder):
    if not os.path.isdir(folder):
        return

    entries.append(folder)
    while len(entries):
        entry = entries.pop()
        temp = str(entry).replace('covid19cubadataactions/', '')
        print("Processing", temp)
        os.system(ftp_command.format(command=mkdir(temp) + 'mput -P 2 ' + entry + '/*;'))
        print("Uploaded", temp)
        if os.path.isdir(entry):
            items = os.listdir(entry)
            for item in items:
                item = entry + '/' + item
                if os.path.isdir(item):
                    entries.append(item)


def run_update(host, user, password):
    global ftp_command
    ftp_command = ftp_command.format_map(LeaveMissing(user=user, password=password, host=host))

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
