#!/usr/bin/python
# coding: UTF-8
# @author Michal Karm Babacek

import re, sys, optparse, time
from nitrate import *
import xmlrpclib

runs = [["Test run ID", "Test run summary", "Test run status"]]
setstatus_testrun_id = 0
setstatus_testcase_ids = []
setstatus_statusname = ""

def logerror(err):
    print color("ProtocolError, we will try it again in 5 seconds.", color="lightred", background="black")
    print "    A protocol error occurred"
    print "    URL: %s" % err.url
    print "    HTTP/HTTPS headers: %s" % err.headers
    print "    Error code: %d" % err.errcode
    print "    Error message: %s" % err.errmsg
    time.sleep(5)

def printRuns(testruns):
    for testrun in testruns:
        sys.stdout.write('█')
        sys.stdout.flush()
        runs.append([str(testrun.id), testrun.summary, testrun.status.name])
        runs.append(["    Test case ID", "    Test case summary", "    Test case status"])
        for caserun in testrun.caseruns:
            if testrun.id == setstatus_testrun_id and str(caserun.testcase.id) in setstatus_testcase_ids:
                old_status = caserun.status
                caserun.status = Status(setstatus_statusname)
                try:
                    caserun.update()
                except xmlrpclib.ProtocolError, err:
                    logerror(err)
                    caserun.update()
                runs.append(["    %s" % str(caserun.testcase.id), "    %s" % str(caserun.testcase.summary), "    %s (was %s)" % (caserun.status.name, old_status.name)])
            else:
                runs.append(["    %s" % str(caserun.testcase.id), "    %s" % str(caserun.testcase.summary), "    %s" % caserun.status.name])
 
if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build BUILD --product \"JBoss EAP\" OPTIONAL: --set_status TESTRUN_ID:TESTCASE_ID,TESTCASE_ID,...")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id", default=5709)
    parser.add_option("--build", dest="build", type="string", help="build name", default="EAP6.1.0.ER4")
    parser.add_option("--product", dest="product", type="string", help="product name", default="JBoss EAP")
    parser.add_option("--set_status", dest="set_status", type="string", help="set status of certain test cases")
    parser.add_option("--set_status_name", dest="set_status_name", type="string", help="PAD IDLE PASSED FAILED RUNNING PAUSED BLOCKED ERROR WAIVED")

    options = parser.parse_args()[0]

    if options.set_status != None:
        setstatus_testrun_id = int(options.set_status.split(":")[0])
        setstatus_testcase_ids = (options.set_status.split(":")[1]).split(",")

    if options.set_status_name != None:
        setstatus_statusname = options.set_status_name

    testplan = TestPlan(options.plan)
    build = Build(id=None, product=options.product, build=options.build)

    msg_runs = "%sRuns created for build %s: %s"

    print color("Warning: This script may take minutes to complete.", color="lightred", background="black")
  
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

    sys.stdout.write(" DONE\n")
    col_width = max(len(word) for row in runs for word in row) + 2
    for row in runs:
        print "".join(word.ljust(col_width) for word in row)