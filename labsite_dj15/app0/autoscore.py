import os
import re
import subprocess
import grade
from account import User
from spec import Assignment, Problem
from upload import Submission, Score

DATA_FILE = 'ungraded_subms'
USE_AUTOGRADER = True
# assignment -> problem -> subms.problem
autograder = User.objects.get(username='autograder')

class EvalInfo:
	score = None
	comment = ''
	def __init__(self, **kwargs):
		for key, val in kwargs.iteritems():
			setattr(self, key, val)

def evaluate(problem, subm):
	MAGIC_COEF1 = 0.9
	MAGIC_COEF2 = 0.85
	totalFileCount = 0
	totalScore = 0
	comments = []
	for type, baseDir, subPath in read_contents(subm, problem):
		if type == '.txt':
			content = open(os.path.join(baseDir, subPath)).read()
			if content:
				score = problem.points
			else:
				score = 0
			comment = ''
		else:
			proc = subprocess.Popen(['cpplint.py', subPath], cwd=baseDir, 
					stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			proc.wait()
			outputLines = proc.stderr.readlines()
			lineCount = len(outputLines)
			errorCountPattern = re.compile('Total errors found: (\d+)')
			try:
				errorCount = int(errorCountPattern.match(outputLines[-1]).group(1))
			except:
				errorCount = 0
			if problem.points == 1:
				score = 1 if errorCount < lineCount * MAGIC_COEF1 else 0
			else:
				score = problem.points - (
						1 if errorCount >= lineCount * MAGIC_COEF2 else 0)
			comment = ''.join(outputLines)
		totalFileCount += 1
		totalScore += score
		comments.append(comment)
	return EvalInfo(score = int(.5 + totalScore / totalFileCount) if totalFileCount else 0,
			comment = '\n'.join(comments))

KnownTypes = ['.cpp', '.cc', '.h', '.cxx', '.hpp', '.c', '.txt', '.mkd']
def detect_type(path):
    base, ext = os.path.splitext(path)
    if ext in KnownTypes:
        return ext
    base, name = os.path.split(path)
    if name.lower() == 'makefile':
        return '.txt'
    return None

def read_contents(subm, problem):
	basePath = os.path.join(subm.decompression.path, 
			subm.assignment.spec.name)
	if problem.type == Problem.CODE:
		dirPath = os.path.join(basePath, problem.name)
		for fname in os.listdir(dirPath):
			try:
				fullpath = os.path.join(dirPath, fname.decode('utf8'))
				type = detect_type(fullpath)
				if type:
					yield type, basePath, os.path.join(problem.name, fname)
			except UnicodeDecodeError:
				pass
	else:
		yield '.txt', basePath, problem.name

def run():
	# auto_assign()
	for subm in Submission.objects.filter(grader=autograder, finished=False):
		for problem in subm.assignment.problems:
			evalInfo = evaluate(problem, subm)
			previous = subm.score_set.filter(problem_name=problem.name)
			if previous is not None: 
				previous.delete()
			score = Score(submission = subm, 
				problem_name = problem.name,
				comment = evalInfo.comment,
				score = evalInfo.score,
			)
			print 'score: ', subm.id, subm.user, subm.assignment.title, problem.name, evalInfo.score 
			score.save()
		subm.finished = True
		subm.save()

def auto_assign():
	for ass in Assignment.objects.all():
		grade.assign(ass, [autograder])

