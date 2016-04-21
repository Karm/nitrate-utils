#!/usr/bin/python

# @author Michal Karm Babacek

import re, sys, optparse, time
from nitrate import *
import xmlrpclib
from sets import Set

NUMBER_OF_TRIALS=5

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
    testers_set = Set()
    for testrun in testruns:
        testers_set.add(testrun.tester.email)
        for trial in range(0, NUMBER_OF_TRIALS):
            try:
                if str(testrun.build) == str(options.build1):
                    matching_runs_counter_build1 = matching_runs_counter_build1 + 1
                if str(testrun.build) == str(options.build2):
                    matching_runs_counter_build2 = matching_runs_counter_build2 + 1
                break
            except xmlrpclib.ProtocolError, err:
                logerror(err)

    return matching_runs_counter_build1, matching_runs_counter_build2, testers_set

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build1 BUILD --build2 BUILD [options]")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id")
    parser.add_option("--build1", dest="build1", type="string", help="build1 name")
    parser.add_option("--build2", dest="build2", type="string", help="build2 name")
    parser.add_option("--no-check-certificate", dest="no_check_certificate", help="Skip verification of Nitrate's SSL certificate", default=False, action="store_true")
    options = parser.parse_args()[0]

    testplan = TestPlan(options.plan)

    overall_counter_build1 = 0
    overall_counter_build2 = 0
    msg_runs = "%sRuns created for build %s: %d %s"
    msg_notify = " Notify %s"
    my_tcms_url = Config().nitrate.url.split("xml")[0]

    print color("Warning: This script may take dozens of minutes to complete :-(", color="lightred", background="black")
  
    if options.no_check_certificate:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

    for testplan in TestPlan.search(parent=testplan.id):
        print "[PLAN] %s %s" % (testplan, testplan.status)
        for trial in range(0, NUMBER_OF_TRIALS):
            try:
                testplan_testruns = testplan.testruns
                break
            except xmlrpclib.ProtocolError, err:
                logerror(err)

        runs_count_build1, runs_count_build2, testers_set = countRuns(testplan_testruns)
        overall_counter_build1 = overall_counter_build1 + runs_count_build1
        overall_counter_build2 = overall_counter_build2 + runs_count_build2

        for trial in range(0, NUMBER_OF_TRIALS):
            try:
                testplan_children = testplan.children
                break
            except xmlrpclib.ProtocolError, err:
                logerror(err)

        if len(testers_set) == 0:
            testers_set.add(testplan.author.email)

        if (runs_count_build1 > runs_count_build2):
            text_color = "yellow"
            notify_author =  ""
            print color(" -> %s%s%s" % (my_tcms_url, "plan/", testplan.id), text_color)
        elif (testplan.status.id == True and runs_count_build1 == 0 and len(testplan_children) == 0):
            text_color = "red"
            notify_author =  msg_notify % str(list(testers_set))
            print color(" -> %s%s%s" % (my_tcms_url, "plan/", testplan.id), text_color)
        else:
            text_color = "green"
            notify_author =  ""

        print color(msg_runs % ('    ', options.build1, runs_count_build1, ""), text_color)
        print color(msg_runs % ('    ', options.build2, runs_count_build2, notify_author), text_color)

        for child in testplan_children:
            print "    [CHILD plan] %s %s" % (child, child.status)

            for trial in range(0, NUMBER_OF_TRIALS):
                try:
                    child_testruns = child.testruns
                    break
                except xmlrpclib.ProtocolError, err:
                    logerror(err)

            runs_count_build1, runs_count_build2, testers_set = countRuns(child_testruns)
            overall_counter_build1 = overall_counter_build1 + runs_count_build1
            overall_counter_build2 = overall_counter_build2 + runs_count_build2

            if len(testers_set) == 0:
                testers_set.add(testplan.author.email)            

            if (runs_count_build1 > runs_count_build2):
                text_color = "yellow"
                notify_author =  ""
                print color("     -> %s%s%s" % (my_tcms_url, "plan/", child.id), text_color) 
            elif (child.status.id == True and runs_count_build1 == 0):
                text_color = "red"
                notify_author =  msg_notify % str(list(testers_set))   
                print color("     -> %s%s%s" % (my_tcms_url, "plan/", child.id), text_color) 
            else:
                text_color = "green"
                notify_author =  ""

            print color(msg_runs % ('        ', options.build1, runs_count_build1, ""), text_color)
            print color(msg_runs % ('        ', options.build2, runs_count_build2, notify_author), text_color)

    print "There are %d runs with build %s and %d runs with build %s." % (overall_counter_build1, options.build1, overall_counter_build2, options.build2)
