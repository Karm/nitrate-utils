#!/usr/bin/python
# coding: UTF-8
# @author Michal Karm Babacek

import re, sys, optparse, time
from nitrate import *
import xmlrpclib
import threading

runs = [["Test run ID", "Test run summary", "Test run status"]]

case_run_status_ids = {}
case_run_status = ""
run_status_ids = []
run_status = ""

"""
On threading: It is disabled, because at 
"""
#worker_threads = []

def logerror(err):
    print color("ProtocolError, we will try it again in 5 seconds.", color="lightred", background="black")
    print "    A protocol error occurred"
    print "    URL: %s" % err.url
    print "    HTTP/HTTPS headers: %s" % err.headers
    print "    Error code: %d" % err.errcode
    print "    Error message: %s" % err.errmsg
    time.sleep(5)

def processInParalel(testrun, setstatus_testcase_ids):
    tmp_runs = []

    if str(testrun.id) in run_status_ids:
        old_status = testrun.status
        testrun.status = RunStatus(run_status)
        try:
            testrun.update()
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            testrun.update()
        tmp_runs.append([str(testrun.id), str(testrun.summary), "%s (was %s)" % (testrun.status.name, old_status.name)])
    else:
        tmp_runs.append([str(testrun.id), str(testrun.summary), testrun.status.name])

    tmp_runs.append(["    Test case ID", "    Test case summary", "    Test case status"])
    for caserun in testrun.caseruns:
        sys.stdout.write('▓')
        sys.stdout.flush()
        if str(caserun.testcase.id) in setstatus_testcase_ids:
            old_status = caserun.status
            caserun.status = Status(case_run_status)
            try:
                caserun.update()
            except xmlrpclib.ProtocolError, err:
                logerror(err)
                caserun.update()
            tmp_runs.append(["    %s" % str(caserun.testcase.id), "    %s" % str(caserun.testcase.summary), "    %s (was %s)" % (caserun.status.name, old_status.name)])
        else:
            tmp_runs.append(["    %s" % str(caserun.testcase.id), "    %s" % str(caserun.testcase.summary), "    %s" % caserun.status.name])
    runs.extend(tmp_runs)

def printRuns(testruns):
    for testrun in testruns:
        sys.stdout.write('▒')
        sys.stdout.flush()
        setstatus_testcase_ids = case_run_status_ids.pop(testrun.id,[None])
        #workerThread = threading.Thread(target=processInParalel, args = (testrun, setstatus_testcase_ids))
        #workerThread.daemon = True
        #workerThread.start()
        #worker_threads.append(workerThread)
        processInParalel(testrun, setstatus_testcase_ids)

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build BUILD --product \"JBoss EAP\" OPTIONAL: --case_run_status_ids \"TESTRUN_ID1:TESTCASE_ID1,TESTCASE_ID2,...;TESTRUN_ID2:TESTCASE_ID1,...\" --case_run_status STATUS --run_status_ids TESTRUN_ID1,TESTRUN_ID2,... --run_status STATUS")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id", default=5709)
    parser.add_option("--build", dest="build", type="string", help="build name", default="EAP6.1.0.ER4")
    parser.add_option("--product", dest="product", type="string", help="product name", default="JBoss EAP")
    parser.add_option("--case_run_status_ids", dest="case_run_status_ids", type="string", help="set status of certain case runs")
    parser.add_option("--case_run_status", dest="case_run_status", type="string", help="PAD, IDLE, PASSED, FAILED, RUNNING, PAUSED, BLOCKED, ERROR, WAIVED")
    parser.add_option("--run_status_ids", dest="run_status_ids", type="string", help="set status of certain runs")
    parser.add_option("--run_status", dest="run_status", type="string", help="RUNNING FINISHED")

    options = parser.parse_args()[0]

    if options.case_run_status_ids != None:
        for one_testrun in options.case_run_status_ids.split(";"):
            case_run_status_ids.update({int(one_testrun.split(":")[0]):(one_testrun.split(":")[1]).split(",")})

    if options.case_run_status != None:
        case_run_status = options.case_run_status

    if options.run_status_ids != None:
        run_status_ids = options.run_status_ids.split(",")

    if options.run_status != None:
        run_status = options.run_status

    testplan = TestPlan(options.plan)
    build = Build(id=None, product=options.product, build=options.build)

    msg_runs = "%sRuns created for build %s: %s"

    print color("Warning: This script may take minutes to complete. I can work in parallel, yet python-nitrate keeps only 1 connection open :-(", color="lightred", background="black")
  
    print "[PLAN] %s %s" % (testplan, testplan.status)

    try:
        testplan_testruns = TestRun.search(plan=testplan.id, build=build.id)
    except xmlrpclib.ProtocolError, err:
        logerror(err)
        testplan_testruns = TestRun.search(plan=testplan.id, build=build.id)

    sys.stdout.write("Loading ")
    sys.stdout.flush()
    try:
        printRuns(testplan_testruns)
    except xmlrpclib.ProtocolError, err:
        logerror(err)
        printRuns(testplan_testruns)

    #for workerThread in worker_threads:
    #    sys.stdout.write('▒')
    #    sys.stdout.flush()
    #    workerThread.join()

    sys.stdout.write(" DONE\n")
    col_width = max(len(word) for row in runs for word in row) + 2
    for row in runs:
        print "".join(word.ljust(col_width) for word in row)