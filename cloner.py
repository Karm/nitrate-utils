#!/usr/bin/python
# coding: UTF-8
# @author Michal Karm Babacek

import re, sys, optparse, time
from nitrate import *
import xmlrpclib

runs = []
case_run_status_ids = {}
case_run_status = ""


def logerror(err):
    print color("ProtocolError, we will try it again in 5 seconds.", color="lightred", background="black")
    print "    A protocol error occurred"
    print "    URL: %s" % err.url
    print "    HTTP/HTTPS headers: %s" % err.headers
    print "    Error code: %d" % err.errcode
    print "    Error message: %s" % err.errmsg
    time.sleep(5)

def logDots(num, char="▒"):
    for _  in range(num):
        sys.stdout.write(char)
        sys.stdout.flush()

def processRuns(testrun, product, new_product_version, new_build, new_tester, new_manager, run_summary_contains, preserve_caseruns):
    logDots(1)
    if run_summary_contains in str(testrun.summary):
        runs.append(["OLD", str(testrun.id), str(testrun.summary), testrun.status.name, str(testrun.build)])
        new_test_run = TestRun(id=None, testplan=testrun.testplan, build=new_build, product=product, version=new_product_version, summary=testrun.summary, notes=testrun.notes, manager=new_manager, tester=new_tester, tags=testrun.tags, testcases=testrun.testcases)
        runs.append(["NEW", str(new_test_run.id), str(new_test_run.summary), new_test_run.status.name, str(new_test_run.build)])
        if preserve_caseruns:
            testrun_caseruns = {}
            for trial in range(0, 5):
                try:
                    testrun_caseruns = {}
                    for caserun in testrun.caseruns:
                        logDots(1,"▓")
                        testrun_caseruns.update({caserun.testcase.id:caserun.status})
                    break
                except xmlrpclib.ProtocolError, err:
                    logerror(err)
            for trial in range(0, 5):
                try:
                    for new_caserun in new_test_run.caseruns:
                        new_caserun.status = testrun_caseruns.get(new_caserun.testcase.id)
                        new_caserun.update()
                        logDots(1)
                    break
                except xmlrpclib.ProtocolError, err:
                    logerror(err)
    else:
        runs.append(["SKIPPED", str(testrun.id), str(testrun.summary), testrun.status.name, str(testrun.build)])
    logDots(1,"▓")

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="./cloner.py --plan 7174 --build \"2.0.0.CR4\" --product \"JBoss EWS\" --new_product_version \"2.1\" --new_build \"2.1.0-ER1\" --new_tester \"shadowman@redhat.com\" --new_manager \"shadowman@redhat.com\"")
    parser.add_option("--plan",                dest="plan",                type="int",    help="test plan id",                default=5709)
    parser.add_option("--build",               dest="build",               type="string", help="build name",                  default="EAP6.3.0.ER4")
    parser.add_option("--product",             dest="product",             type="string", help="product name",                default="JBoss EAP")
    parser.add_option("--new_product_version", dest="new_product_version", type="string", help="product version name",        default="6.0")
    parser.add_option("--new_build",           dest="new_build",           type="string", help="new build name",              default="EAP6.3.0.ER5")
    parser.add_option("--new_tester",          dest="new_tester",          type="string", help="new tester",                  default="shadowman@redhat.com")
    parser.add_option("--new_manager",         dest="new_manager",         type="string", help="new manager",                 default="shadowman@redhat.com")
    parser.add_option("--run_summary_contains",dest="run_summary_contains",type="string", help="run summary contains",        default=None)
    parser.add_option("--preserve_caseruns",   dest="preserve_caseruns",   type="string",help="preserve old caseruns states",default=False)

    options = parser.parse_args()[0]
    print color("Warning: This script may take minutes to complete.", color="lightred", background="black")
    sys.stdout.write("Loading ...\n")
    sys.stdout.flush()
    testplan = TestPlan(options.plan)
    sys.stdout.write("[PLAN] %s %s " % (testplan, testplan.status))
    sys.stdout.flush()
    logDots(1)
    build = Build(id=None, product=options.product, build=options.build)
    logDots(2)
    new_build = Build(id=None, product=options.product, build=options.new_build)
    logDots(3)
    new_product_version = Version(id=None, name=options.new_product_version, product=options.product)
    logDots(4)
    new_tester = User(id=None, login=None, email=options.new_tester)
    logDots(5)
    new_manager = User(id=None, login=None, email=options.new_manager)
    logDots(6)

    try:
        testplan_testruns = TestRun.search(plan=testplan.id, build=build.id)
    except xmlrpclib.ProtocolError, err:
        logerror(err)
        for trial in range(0, 5):
            try:
                testplan_testruns = TestRun.search(plan=testplan.id, build=build.id)
                break
            except xmlrpclib.ProtocolError, err:
                logerror(err)

    runs = [["RUN", "Test run ID", "Test run summary", "Status", "Build"]]
    for testrun in testplan_testruns:
        try:
            processRuns(testrun, options.product, new_product_version, new_build, new_tester, new_manager, options.run_summary_contains, options.preserve_caseruns)
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            for trial in range(0, 5):
                try:
                    processRuns(testrun, options.product, new_product_version, new_build, new_tester, new_manager, options.run_summary_contains, options.preserve_caseruns)
                    break
                except xmlrpclib.ProtocolError, err:
                    logerror(err)

    sys.stdout.write(" DONE\n")
    col_width = []
    for i in range(max(len(row) for row in runs)):
        col_width.append(0)
    for row in runs:
        for index,word in enumerate(row):
            col_width[index] = max(len(word)+2,col_width[index])
    for row in runs:
        print "".join(word.ljust(col_width[index]) for index,word in enumerate(row))
