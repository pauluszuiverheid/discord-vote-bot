'''
Script to streamline updates

file "update-config.json" should have:
{
    "user": "",
    "password": "",
    "email": "",
    "repository": "ChemicalXandco/discord-vote-bot",
    "ssh": false,
}
if ssh is true, add:
    "ssh_ip": "",
    "ssh_user": "",
    "ssh_password": ""
'''

from github import Github
from github.InputGitAuthor import InputGitAuthor
from datetime import datetime
import json

config = json.loads(open('update-config.json').read())

botConfig = json.loads(open('data/config.json').read())

version = input('What version? {} -> '.format(botConfig['version']))

if version != botConfig['version']:
    package = json.loads(open('package.json').read())
    package['version'] = version
    with open('package.json', 'w') as f:
            json.dump(package, f, indent=4)
            f.close()

    try:
        blankConfig = botConfig.copy()
        blankConfig.update({'token': '',
                            'prefix': 'vb!',
                            'version': version})
        with open('data/config.json', 'w') as f:
            json.dump(blankConfig, f, indent=4)
            f.close()

        input('Double tap enter when pushed changes...')
        input('')

        g = Github(config['user'], config['password'])
        repo = g.get_repo(config['repository'])

        message = 'Tag created at {}'.format(
                datetime.now().strftime('%b %d, %Y %H:%M'))

        branch = repo.get_branch('master')
        sha = repo.get_commits(branch.commit.sha)[0].sha

        tagger = InputGitAuthor(
            name=config['user'],
            email=config['email'],
            date=datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        t = repo.create_git_tag('v{}'.format(version),
                       message,
                       sha,
                       'commit',
                       tagger)
        repo.create_git_ref('refs/tags/{}'.format(t.tag), t.sha)
        print('tag create success')
    except Exception as e:
        print('Error:', str(e))
        version = botConfig['version']
    finally:
        with open('data/config.json', 'w') as f:
            botConfig['version'] = version
            json.dump(botConfig, f, indent=4)
            f.close()

if config['ssh']:
    print('ssh start')
    import paramiko

    commands = [
        'git fetch',
        'git stash push --keep-index --include-untracked -m "cleaning_before_git_hook"',
        'git pull',
        'git reset --hard',
        'git stash pop --index',
        'sudo reboot'
        ]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
    client.connect(config['ssh_ip'], username=config['ssh_user'], password=config['ssh_password'])
    
    for command in commands:
        stdin, stdout, stderr = client.exec_command('cd vb; '+command)
        for line in stdout:
            print('... ' + line.strip('\n'))
        for line in stderr:
            print('... ' + line.strip('\n'))

    client.close()

    print('ssh complete')
