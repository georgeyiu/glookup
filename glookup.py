#!/usr/bin/python

import os
import re
import sys
import pickle
import getopt
import getpass
import paramiko

def download():
    ''' Retrieves and saves all glookup data from servers '''

    while True:
        try:
            user = raw_input('username: ')
            server = 'hive3.cs.berkeley.edu'  #raw_input('server: ')
            passwd = getpass.getpass('password: ')

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            ssh.connect(server, username=user, password=passwd)
            break
        except paramiko.AuthenticationException:
            print 'Permission denied, please try again.'

    stdin, stdout, stderr = ssh.exec_command('glookup')
    glookup_data = stdout.read()
    lines = glookup_data.split('\n')
    firstline = lines[0]
    classname = firstline[:firstline.find('-')]
    dirname = classname + '_grades'
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(os.path.join(dirname, 'glookup.txt'), 'w') as f:
        f.write(glookup_data)

    data = {}
    for line in lines[2:]:
        assignment = line.split(':')[0].strip()
        command = 'glookup -s ' + assignment + ' -b 0.1'
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read()
        with open(os.path.join(dirname, assignment + '.txt'), 'w') as f:
            f.write(output)
        output = output.split('\n')
        scores = []
        my_score = 0
        if len(output) > 1:
            my_score = None
            match = re.search(r'Your score:[\s]*([0-9.]+)[\s]*', output[1])
            if match:
                my_score = match.group(1)
        for l in output:
            match = re.match(r'([\s]*[0-9.]+)[\s-]*[0-9.]+:[\s]*([0-9]+)', l)
            if match:
                scores += [float(match.group(1))] * int(match.group(2))
        data[assignment] = (my_score, scores)   
        if assignment == 'Total':
            break

    ssh.close()
    pickle.dump(data, open(classname + '.p', 'wb'))

def stats(f, assignment):
    ''' 
    Displays statistics for a particular assignment.
    Usage is such as 'gloookup -s <assignment>'
    '''
    
    data = pickle.load(open(f, 'rb'))
    d = data.get(assignment)
    if d == None:
        print 'There is no assignment {0}.'.format(assignment)
        sys.exit(2)
    my_score = d[0]
    scores = d[1]
    print 'Your score: {0}'.format(my_score)
    print 'Mean: {0}'.format(sum(scores)/len(scores))

def main(argv):
    # TODO: Fix arguments and usage strings. 
    try:
        opts, args = getopt.getopt(argv,"df:s:b:")
    except getopt.GetoptError:
        print 'test.py -d -f <filename> -s <assignment> -b <bucket_size>'
        sys.exit(2)
    filename = ''
    for opt, arg in opts:
        if opt == '-f':
            filename = arg
        elif opt == '-s':
            if not filename:
                print 'Usage: glookup.py -d -f <filename> -s <assignment> -b <bucket_size>'    
                sys.exit()
            stats(filename, arg)
        elif opt == '-b':
            print 'buckets not implemented'
        elif opt == '-d':
            download()

if __name__ == "__main__":
   main(sys.argv[1:])

