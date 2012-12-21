#!/usr/bin/python

# @author Michal Karm Babacek

import re, sys, optparse
from nitrate import *

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build BUILD [options]")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id")
    parser.add_option("--build", dest="build", type="string", help="build name")
    options = parser.parse_args()[0]

    testplan = TestPlan(options.plan)

overall_counter = 0
for testplan in TestPlan.search(parent=testplan.id):
    print testplan, testplan.status
    matching_runs_counter = 0
    for testrun in testplan.testruns:
        if str(testrun.build) == str(options.build):
            matching_runs_counter = matching_runs_counter + 1
    print "Runs created for build %s: %d" % (options.build, matching_runs_counter)
    overall_counter = overall_counter + matching_runs_counter

print "For all the test plans, there are %d runs with build %s" % (overall_counter, options.build)
