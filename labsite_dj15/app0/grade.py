from django.db import models
from django.utils import timezone
from upload import Submission, Score
from subprocess import Popen, PIPE
from datetime import datetime
from threading import Thread
from time import sleep, clock
from select import select
import logging

logger = logging.getLogger(__name__)

class Run(models.Model):
    INTERACT_TIMEOUT = 5
    procs = {}
    """
    state: running, finished.
    """
    procID = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    start_time = models.DateTimeField(auto_now_add=True)

    # def __init__(self, *args, **kwargs):
    #     super(Run, self).__init__(*args, **kwargs)

    @property
    def proc(self):
        return Run.procs.get(int(self.procID), None)

    def interact(self, data=None):
        proc = self.proc
        if proc is None:
            return (137, '', 'Process killed')
        retcode = proc.poll()
        if retcode is not None:
            return (retcode, proc.stdout.read(), proc.stderr.read())
        if data is not None:
            proc.stdin.write(data)
        dataOut, dataErr = '', ''
        que = [proc.stdout, proc.stderr]
        timeout = self.INTERACT_TIMEOUT
        startClock = clock()
        while que:
            readReady, _, _ = select(que, [], [], 0.02)
            if not  readReady:
                break
            for st in readReady:
                if st == proc.stdout:
                    c = st.read(1)
                    if c: dataOut += c
                    else: que.remove(st)
                elif st == proc.stderr:
                    c = st.read(1)
                    if c: dataErr += c
                    else: que.remove(st)
            clk = clock()
            if clk - startClock > timeout: break

        return (proc.poll(), dataOut, dataErr)

    def stop(self):
        proc = self.proc
        if proc and proc.poll() is None:
            # proc not ended
            proc.kill()
        self.state = '137'
        self.save()

    def delete(self):
        logger.debug('runID {} delete'.format(self.id))
        self.stop()
        try: del Run.procs[int(self.procID)]
        except KeyError: pass
        super(Run, self).delete()

def run(compilation, args=None):
    # return an run instance
    cmd = [compilation.exe]
    if args:
        cmd.extends(args)
    proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    # proc.daemon = True
    Run.procs[proc.pid] = proc
    prog = Run(procID=proc.pid, state='')
    prog.save()
    # DEBUG
    logger.debug('runID {} start'.format(prog.id))
    return prog

def clear():
    TIME_OUT = 5 * 60
    INTERVAL = 2
    while 1:
        sleep(INTERVAL)
        now = timezone.now()
        for run in Run.objects.filter(state=''):
            logger.debug("now:{} run.start_time:{} secs:{}".format(now, run.start_time, (now - run.start_time).total_seconds()))
            if (now - run.start_time).total_seconds() > TIME_OUT:
                run.stop()

def assign(assignment, TAs):
    submissions = filter_last(Submission.objects.filter(retcode=0, assignment=assignment))
    cnt = {ta: 0 for ta in TAs}
    for subm in submissions:
        if subm.finished:
            if subm.grader in cnt:
                cnt[subm.grader] += 1
    for subm in submissions:
        if not subm.finished:
            grader = min(cnt.items(), key=lambda (u, c): c)[0]
            cnt[grader] += 1
            subm.grader = grader
            subm.save()

def filter_last(submissions):
    subms = {}
    for subm in submissions:
        if subm.user in subms:
            old = subms[subm.user]
            if subm.time > old.time:
                subms[subm.user] = subm
            else:
                old = subm
            if not old.finished:
                old.grader = None
                old.save()
        else:
            subms[subm.user] = subm
    return subms.values()

def start_clear():
    th = Thread(target=clear)
    th.daemon = True
    th.start()
start_clear()
