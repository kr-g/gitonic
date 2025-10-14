import sys
import time


class CmdRunner(object):
    def __init__(self):
        self.done = False

        self.err = False
        self.err_detail = None

    def complete(self, tout=0.001):
        while self.loop():
            time.sleep(tout)
        return self

    def loop(self):
        return True

    def setdone(self):
        assert self.done is False
        self.done = True


class RepoTaskRunner(CmdRunner):
    def __init__(self, repo, repo_task_it):
        CmdRunner.__init__(self)

        self.repo = repo
        self.repo_task_it = repo_task_it

        self.cmd = None

    def loop(self):
        if self.err or self.done:
            return False

        # print("run", self.repo)

        if self.cmd is None:
            try:
                if self.repo_task_it:
                    self.cmd = next(self.repo_task_it)
                    rc = self.cmd.start()
                    if rc:
                        raise Exception("start failed", str(self.repo_task_it))
                    return True

            except StopIteration:
                return False

            except Exception as ex:
                self.err = True
                self.err_detail = ex
                print("task run err: loop", str(
                    self.repo), ex, file=sys.stderr)
                return False

        if self.cmd.running() is False:
            # remove and continue with next command
            self.cmd = None
        return True


class PoolTaskRunner(object):
    def __init__(self, it_task_runner, maxthreads=0):
        self.tasks = list(it_task_runner)
        self.total_tasks = len(self.tasks)
        self.maxthreads = maxthreads
        self.curtasks = []

    def _balance_tasks(self):

        self.curtasks = list(
            filter(lambda x: x.done is False, self.curtasks))

        # print()
        # print("pool",self,len(self.tasks), len(self.curtasks))
        # print()

        while len(self.tasks) > 0 and (
            len(self.curtasks) < self.maxthreads or
            self.maxthreads <= 0
        ):
            # print("add to pool, remain",len(self.tasks))

            self.curtasks.append(self.tasks.pop(0))

    def loop(self):
        cnt = 0
        try:
            self._balance_tasks()
        except Exception as ex:
            print("!!!balance", ex)
        for repotasks in self.curtasks:
            if repotasks.done or repotasks.err:
                cnt += 1
                continue
            if repotasks.loop() is False:
                repotasks.setdone()
        return (len(self.curtasks) + len(self.tasks)) > 0
