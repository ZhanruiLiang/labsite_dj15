from django.db import models
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
    start_time = models.DateTimeField(auto_now=True)

    # def __init__(self, *args, **kwargs):
    #     super(Run, self).__init__(*args, **kwargs)

    @property
    def proc(self):
        return Run.procs[int(self.procID)]

    def interact(self, data=None):
        proc = self.proc
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

        if proc.poll() is not None:
            # ended
            self.stop()
        return (dataOut, dataErr)

    def stop(self):
        if self.proc.poll() is None:
            # proc not ended
            self.proc.kill()
            self.state = proc.poll()
            self.save()

    def delete(self):
        # logger.debug('runID {} delete'.format(self.id))
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
    # logger.debug('runID {} start'.format(prog.id))
    return prog

def clear():
    TIME_OUT = 5 * 60
    INTERVAL = 60
    while 1:
        sleep(INTERVAL)
        now = datetime.today()
        for run in Run.objects.all():
            if (now - run.start_time).seconds > TIME_OUT:
                run.stop()

def start_clear():
    Thread(target=clear).start()
# start_clear()
