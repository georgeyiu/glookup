#!/usr/bin/python

import os
import re
import sys
import math
import pickle
import argparse
import getpass
import paramiko
from collections import Counter

def fetch():
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

	data = {}
	stdin, stdout, stderr = ssh.exec_command('glookup')
	glookup_data = stdout.read()
	lines = glookup_data.split('\n')
	data['glookup'] = lines
	firstline = lines[0]
	classname = firstline[:firstline.find('-')]

	for line in lines[2:]:
		assignment = line.split(':')[0].strip()
		command = 'glookup -s ' + assignment + ' -b 0.1'
		stdin, stdout, stderr = ssh.exec_command(command)
		output = stdout.read().split('\n')
		scores = []
		my_score = 0
		if len(output) > 1:
			my_score = None
			match = re.search(r'Your score:[\s]*([0-9.]+)[\s]*', output[1])
			if match:
				my_score = match.group(1)
			max_score = None
			match = re.search(r'Max possible:[\s]*([0-9.]+)', output[10])
			if match:
				max_score = match.group(1)
		for l in output:
			match = re.match(r'([\s]*[0-9.]+)[\s-]*[0-9.]+:[\s]*([0-9]+)', l)
			if match:
				scores += [float(match.group(1))] * int(match.group(2))
		data[assignment] = (my_score, max_score, scores)   
		if assignment == 'Total':
			break

	ssh.close()
	pickle.dump(data, open(classname + '.p', 'wb'))


def print_stats(data, assignment, bucketsize):
	''' Displays statistics for a particular assignment '''

	def average(s): return sum(s) * 1.0 / len(s)

	if not assignment:
		glookup_output = data['glookup']
		for line in glookup_output:
			print line.rstrip()
		return
	d = data.get(assignment)
	if not d:
		print 'There is no assignment {0}.'.format(assignment)
		sys.exit(2)

	scores = d[2]
	num_scores = len(scores)

	your_score = d[0]
	mean = round(average(scores), 1)
	mode = Counter(scores).most_common(1)[0][0]
	minimum = scores[0]
	first_quartile = scores[num_scores/4]  # estimate, should find exact
	second_quartile = scores[num_scores/2]
	third_quartile = scores[int(round(num_scores/4.0*3))]
	maximum = scores[-1]
	max_possible = d[1]

	stdev = round(math.sqrt(average(map(lambda x: (x - mean)**2, scores))), 1)
	rank = list(reversed(scores)).index(float(your_score)) + 1

	print 'Your score: {0:>20}  (#{1} out of {2})'.format(your_score, rank, num_scores)
	print 'Mean: {0:>26}'.format(mean)
	print 'Mode: {0:>26}'.format(mode)
	print 'Standard deviation: {0:>12}'.format(stdev)
	print 'Minimum: {0:>23}'.format(minimum)
	print '1st quartile: {0:>18}'.format(first_quartile)
	print '2nd quartile (median): {0:>9}'.format(second_quartile)
	print '3rd quartile: {0:>18}'.format(third_quartile)
	print 'Maximum: {0:>23}'.format(maximum)
	print 'Max possible: {0:>18}'.format(max_possible)
	print 'Distribution:'
	
	if not bucketsize:
		bucketsize = math.floor(maximum/25.0)

	start_len = None
	end_len = None
	max_count = 0
	buckets = []
	start = 0
	end = bucketsize
	score = scores.pop(0)
	while (start <= maximum):
		count = 0
		while start <= score and score < end:
			count += 1
			if not scores:
				break
			score = scores.pop(0)
		if count > max_count:
			max_count = count
		buckets.append((round(start, 1), count))
		start += bucketsize
		end += bucketsize

	start_format = '{0:>' + str(len(str(start))) + '}'
	end_format = '{1:>' + str(len(str(end))) + '}'
	for (start, count) in buckets:
		stars = '*'*int(math.ceil(count*1.0/max_count*20))
		full_format = start_format + ' - ' + end_format + ':{2:>5} {3}'
		print full_format.format(start, start + bucketsize, count, stars)


def main(argv):
	''' Parse arguments '''

	parser = argparse.ArgumentParser(description='glookup')
	parser.add_argument('-c', '--course', help='filepath to fetched data')
	parser.add_argument('-f', '--fetch', action='store_true', 
						help='fetch glookup data')
	parser.add_argument('-s', '--assignment', action='store', 
						help='specify an assignment')
	parser.add_argument('-b', '--bucket', action='store', type=float, dest='bucket',
						help='specify a bucket size')
	args = parser.parse_args()

	if args.fetch:
		fetch()
	elif args.course:
		if args.bucket and not args.assignment:
			parser.error('-b must be used with -s')
		try:
			data = pickle.load(open(args.course, 'rb'))
		except:
			parser.error("invalid file {0}. Select data file \
				fetched by 'glookup -f'".format(args.course))
		print_stats(data, args.assignment, args.bucket)
	else:
		parser.error('-c or -f is required')


if __name__ == "__main__":
   main(sys.argv[1:])

