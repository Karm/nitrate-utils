#!/usr/bin/python

# @author Michal Karm Babacek

import re, sys, optparse, time
from nitrate import *
import xmlrpclib

def logerror(err):
    print color("ProtocolError, we will try it again in 5 seconds.", color="lightred", background="black")
    print "    A protocol error occurred"
    print "    URL: %s" % err.url
    print "    HTTP/HTTPS headers: %s" % err.headers
    print "    Error code: %d" % err.errcode
    print "    Error message: %s" % err.errmsg
    time.sleep(5)

def countRuns(testruns):
    matching_runs_counter = 0
    for testrun in testruns:
        try:
            if str(testrun.build) == str(options.build):
                matching_runs_counter = matching_runs_counter + 1
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            if str(testrun.build) == str(options.build):
                matching_runs_counter = matching_runs_counter + 1
    return matching_runs_counter

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build BUILD [options]")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id")
    parser.add_option("--build", dest="build", type="string", help="build name")
    options = parser.parse_args()[0]

    testplan = TestPlan(options.plan)

    overall_counter = 0

    print color("Warning: This script may take dozens of minutes to complete :-(", color="lightred", background="black")
  
    for testplan in TestPlan.search(parent=testplan.id):
        print "[PLAN] %s %s" % (testplan, testplan.status)

        try:
            testplan_testruns = testplan.testruns
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            testplan_testruns = testplan.testruns

        runs_count = countRuns(testplan_testruns)
        
        overall_counter = overall_counter + runs_count
        print "    Runs created for build %s: %d" % (options.build, runs_count)

        try:
            testplan_children = testplan.children
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            testplan_children = testplan.children

        for child in testplan_children:
            print "    [CHILD plan] %s %s" % (child, child.status)

            try:
                child_testruns = child.testruns
            except xmlrpclib.ProtocolError, err:
                logerror(err)
                child_testruns = child.testruns

            runs_count = countRuns(child_testruns)
            overall_counter = overall_counter + runs_count
            print "        Runs created for build %s: %d" % (options.build, runs_count)
    
    print "For all the test plans, there are %d runs with build %s" % (overall_counter, options.build)