#!/usr/bin/python

import os
import re
import sys
import math
import pickle
import getpass
import argparse
import paramiko
from collections import Counter, defaultdict

def fetch_data():
	''' 
	Retrieves glookup data of provided account credentials and saves
	all data in a file with the name of the class in the local directory.
	'''

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

	data = {}
	stdin, stdout, stderr = ssh.exec_command('glookup')
	glookup_data = stdout.read()
	lines = glookup_data.split('\n')
	data['glookup'] = lines
	line1 = lines.pop(0)
	line2 = lines.pop(0)
	classname = line1.split('-')[0]

	for line in lines:
		assignment = line.split(':')[0].strip()
		command = 'glookup -s ' + assignment + ' -b 0.1'
		stdin, stdout, stderr = ssh.exec_command(command)
		output = stdout.read().split('\n')

		if len(output) <= 1:
			data[assignment] = (0, 0, [])
			continue

		scores = []
		my_score = re.search(r'Your score:[\s]*([0-9.]+)[\s]*', output[1]).group(1)
		max_possible = re.search(r'Max possible:[\s]*([0-9.]+)', output[10]).group(1)
		for l in output:
			match = re.match(r'([\s]*[0-9.]+)[\s-]*[0-9.]+:[\s]*([0-9]+)', l)
			if match:
				scores += [float(match.group(1))] * int(match.group(2))
		data[assignment] = (my_score, max_score, scores)   
		if assignment == 'Total':
			break

	ssh.close()
	pickle.dump(data, open(classname, 'wb'))
	print "Success: data saved in file: " + classname


def print_stats(data, assignment, bucketsize):
	''' Displays statistics for a particular assignment '''

	def average(s): 
		return sum(s) * 1.0 / len(s)

	def format32(msg, arg):
		return msg + str(arg).rjust(32 - len(msg))

	def find_median(lst, num_elements):
		lower = int(num_elements - 0.5)
		upper = int(num_elements)
		return round(average([lst[lower], lst[upper]]), 1)

	def find_bucket(score):
		return int(score/bucketsize)*bucketsize

	if not assignment:
		glookup_output = data['glookup']
		for line in glookup_output:
			print line.rstrip()
		return

	if not data.get(assignment):
		print 'There is no assignment {0}.'.format(assignment)
		return

	(your_score, max_possible, scores) = data[assignment]

	if not scores:
		print 'Not enough scores have been entered for this assignment'
		return

	num_scores = len(scores)
	rank = scores[::-1].index(float(your_score)) +  1
	mean = round(average(scores), 1)
	counts = Counter(scores).most_common()
	mode, occurences = counts[0]
	ambiguous = [x[1] for x in counts].count(occurences) > 1
	stdev = round(math.sqrt(average(map(lambda x: (x - mean)**2, scores))), 1)
	minimum = scores[0]
	q1 = find_median(scores, num_scores/4.0)
	q2 = find_median(scores, num_scores/2.0)
	q3 = find_median(scores, num_scores/4.0*3)
	maximum = scores[-1]

	print data['glookup'][0].rstrip()
	print format32('Your score:', your_score),
	print ' (#{0} out of {1})'.format(rank, num_scores)
	print format32('Mean:', mean)
	print format32('Mode:', mode), 
	print '(ambiguous)' if ambiguous else ''
	print format32('Standard deviation:', stdev)
	print format32('Minimum:', minimum)
	print format32('1st quartile:', q1)
	print format32('2nd quartile (median):', q2)
	print format32('3rd quartile:', q3)
	print format32('Maximum:', maximum)
	print format32('Max possible:', max_possible)
	print 'Distribution:'
	
	bucketsize = max(bucketsize, 0.1) if bucketsize else math.ceil(maximum/25.0)

	bucket_dict = defaultdict(int)
	for x in scores:
		bucket_dict[find_bucket(x)] += 1

	largest_bucket = max(bucket_dict.values())
	start, end = find_bucket(minimum), find_bucket(maximum)

	start_format = '{0:>' + str(len(str(end))+1) + '}'
	end_format = '{1:>' + str(len(str(end+bucketsize))) + '}'
	full_format = start_format + ' - ' + end_format + ':{2:>5} {3}'

	while start <= end:
		count = bucket_dict.get(start, 0)
		stars = '*' * int(math.ceil(20*(count*1.0/largest_bucket)))
		print full_format.format(start, start+bucketsize-0.1, count, stars)
		start += bucketsize


def parse_arguments():
	''' Parse arguments '''

	parser = argparse.ArgumentParser(description='glookup')
	parser.add_argument('-f', '--fetch', action='store_true',
						help='fetch glookup data') 
	parser.add_argument('-c', '--course', help="path to file created by 'glookup -f'")
	parser.add_argument('-s', '--assignment', action='store', 
						help='specify an assignment')
	parser.add_argument('-b', '--bucket', action='store', type=float, 
						dest='bucket', help='specify a bucket size')
	
	args = parser.parse_args()
	if args.fetch:
		fetch_data()
	elif args.course:
		if args.bucket and not args.assignment:
			parser.error('-b must be used with -s')
		try:
			data = pickle.load(open(args.course, 'rb'))
		except:
			parser.error("invalid file provided to -c".format(args.course))
		print_stats(data, args.assignment, args.bucket)
	else:
		parser.error('-c or -f is required')


if __name__ == "__main__":
   parse_arguments()
