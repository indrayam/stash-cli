import codecs
import shlex
import sys
from subprocess import Popen, PIPE


def create_repo(ulist, encpwd):
    """
    :param ulist: List of users
    :param encpwd: Encoded password for Stash
    :return: None
    """

    # Set clean_existing_repos value based on your training needs. By default it will NOT delete existing repos
    clean_existing_repos = False
    count = 0
    count_new = 0
    non_existent_user = []
    password = codecs.decode(encpwd, 'rot_13')
    for user in ulist:
        count += 1

        # Does the user exist? This is ONLY required for reporting if the end user will be able to access Stash
        cmd = './stash.sh -s https://gitscm.cisco.com -u automation -p ' + password + \
              ' -a getUser --userId ' + user
        args = shlex.split(cmd)
        p = Popen(args,
                  stdout=PIPE, stderr=PIPE, cwd=folder_path('home', user))
        output, err = p.communicate()
        rc = p.returncode
        if rc > 0:
            non_existent_user += [user]
            print(err.decode('utf-8'), end='')
            print('-' * 50)
        else:
            print(output.decode('utf-8'), end='')
            print(count, ":", user, "[User Exist check complete]")
            print('-' * 50)

        # Delete the Repo
        if clean_existing_repos:
            cmd = './stash.sh -s https://gitscm.cisco.com -u automation -p ' + password + \
                  ' -a deleteRepository --project TTTS -r ' + reponame(user)
            args = shlex.split(cmd)
            p = Popen(args,
                      stdout=PIPE, stderr=PIPE, cwd=folder_path('home', user))
            output, err = p.communicate()
            rc = p.returncode
            print(output.decode('utf-8'), end='')
            if rc > 0:
                print(err.decode('utf-8'), end='')
            print(count, ":", user, "[Repo Deleted]")

        # Set the default value of repo_exist to False. Meaning create the repo if it does not exist
        repo_exist = False

        # Check repo_exist iff clean_existing_repos setting is False
        if not clean_existing_repos:
            cmd = './stash.sh -s https://gitscm.cisco.com -u automation -p ' + password + \
                  ' -a getRepository --project TTTS -r ' + reponame(user)
            args = shlex.split(cmd)
            p = Popen(args,
                      stdout=PIPE, stderr=PIPE, cwd=folder_path('home', user))
            output, err = p.communicate()
            rc = p.returncode
            if rc > 0:
                print(err.decode('utf-8'), end='')
            else:
                repo_exist = True
                print(output.decode('utf-8'), end='')
                print(count, ":", user, "[Repo check complete]")

        # Do the next steps iff repo_exist is False
        if not repo_exist:
            count_new += 1
            cmd = './stash.sh -s https://gitscm.cisco.com -u automation -p ' + password + ' -a createRepository ' + \
                  '--project TTTS -r ' + reponame(user)
            args = shlex.split(cmd)
            p = Popen(args,
                      stdout=PIPE, stderr=PIPE, cwd=folder_path('home', user))
            output, err = p.communicate()
            rc = p.returncode
            print(output.decode('utf-8'), end='')
            if rc > 0:
                print(err)
            print(count, ":", user, "[Repo Created]")
        else:
            print('-' * 75)
            print("Skipping processing for", user, "since the repo", reponame(user), "already exists")
            print('-' * 75)

    # Wrap up
    final_wrap_up(non_existent_user, count, count_new)


def folder_path(leaf, user):
    """
    :param leaf: Custom string to qualify which folder path to return
    :param user: User Id
    :return: Folder Path to be used as current working directory
    """
    path = ''
    if leaf == 'repo':
        path += '/Users/anand/workspace/_python_/python-projects/ttt-stash-cli/tmp/' + reponame(user)
    elif leaf == 'repo_parent':
        path += '/Users/anand/workspace/_python_/python-projects/ttt-stash-cli/tmp/'
    elif leaf == 'home':
        path += '/Users/anand/workspace/_python_/python-projects/ttt-stash-cli/'

    return path


def reponame(userid):
    """
    :param userid: User ID
    :return: Repo Name (append -ttt to the UserID passed)
    """
    return userid + '-ttt'


def final_wrap_up(nousrlist, c, c_new):
    f = open('/tmp/non-existent-users.txt', 'w')
    count = 0
    for user in nousrlist:
        count += 1
        f.write(user + '\n')
    f.close()
    print()
    print('+' * 100)
    print("Number of total users in the input file:", c)
    print("Number of users from total users whose repo got created during this run:", c_new)
    print("Number of users that do not exist in Atlassian Stash:", count)
    print("\tFor more information, see /tmp/non-existent-users.txt file")
    print('+' * 100)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: {} password'.format(sys.argv[0]))
        sys.exit(1)
    else:
        # You did not think I was going to give you the password that easy ;-)
        encoded_password = sys.argv[1]

        # Read the list of trainees from the external text file
        f = open('trainees.txt', 'r')
        userlist = []
        for line in f:
            userlist.append(line.rstrip())
        f.close()

        # Let's create the repos, shall we?
        create_repo(userlist, encoded_password)