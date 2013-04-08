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
    matching_runs_counter_build1 = 0
    matching_runs_counter_build2 = 0
    for testrun in testruns:
        try:
            if str(testrun.build) == str(options.build1):
                matching_runs_counter_build1 = matching_runs_counter_build1 + 1
            if str(testrun.build) == str(options.build2):
                matching_runs_counter_build2 = matching_runs_counter_build2 + 1
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            if str(testrun.build) == str(options.build1):
                matching_runs_counter_build1 = matching_runs_counter_build1 + 1
            if str(testrun.build) == str(options.build2):
                matching_runs_counter_build2 = matching_runs_counter_build2 + 1
    return matching_runs_counter_build1, matching_runs_counter_build2

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build1 BUILD --build2 BUILD [options]")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id")
    parser.add_option("--build1", dest="build1", type="string", help="build1 name")
    parser.add_option("--build2", dest="build2", type="string", help="build2 name")
    options = parser.parse_args()[0]

    testplan = TestPlan(options.plan)

    overall_counter_build1 = 0
    overall_counter_build2 = 0
    msg_runs = "%sRuns created for build %s: %d %s"
    msg_notify = " Notify %s"

    print color("Warning: This script may take dozens of minutes to complete :-(", color="lightred", background="black")
  
    for testplan in TestPlan.search(parent=testplan.id):
        print "[PLAN] %s %s" % (testplan, testplan.status)

        try:
            testplan_testruns = testplan.testruns
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            testplan_testruns = testplan.testruns

        runs_count_build1, runs_count_build2 = countRuns(testplan_testruns)
        
        overall_counter_build1 = overall_counter_build1 + runs_count_build1
        overall_counter_build2 = overall_counter_build2 + runs_count_build2

        if runs_count_build1 != runs_count_build2:
            text_color = "red"
            notify_author =  msg_notify % testplan.author.email
        else:
            text_color = "green"
            notify_author =  ""

        print color(msg_runs % ('    ', options.build1, runs_count_build1, ""), text_color)
        print color(msg_runs % ('    ', options.build2, runs_count_build2, notify_author), text_color)

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

            runs_count_build1, runs_count_build2 = countRuns(child_testruns)
            overall_counter_build1 = overall_counter_build1 + runs_count_build1
            overall_counter_build2 = overall_counter_build2 + runs_count_build2
            if runs_count_build1 != runs_count_build2:
                text_color = "red"
                notify_author =  msg_notify % testplan.author.email
            else:
                text_color = "green"
                notify_author =  ""

            print color(msg_runs % ('    ', options.build1, runs_count_build1, ""), text_color)
            print color(msg_runs % ('    ', options.build2, runs_count_build2, notify_author), text_color)

    print "There are %d runs with build %s and %d runs with build %s." % (overall_counter_build1, options.build1, overall_counter_build2, options.build2)
