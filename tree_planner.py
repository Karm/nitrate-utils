#!/usr/bin/python

# @author Michal Karm Babacek

import re, sys, optparse
from nitrate import *

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build BUILD [options]")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id")
    parser.add_option("--build", dest="build", type="int", help="build id")
    options = parser.parse_args()[0]

our_testplans = {}
new_parent_plan = TestPlan(options.plan)

for testrun in TestRun.search(build=options.build):
    our_testplans[testrun.testplan.id] = testrun.testplan
print "--------------------------------TEST PLANS---------------------------------"
for key in our_testplans.keys():
    print "Test plan ID: %d | Test plan name: %s" % (key, our_testplans[key])
    print "    Parent: %s" % our_testplans[key].parent
    if our_testplans[key].parent is not None:
        print "        Grandparent: %s" % our_testplans[key].parent.parent
        if our_testplans[key].parent.id != new_parent_plan.id and our_testplans[key].parent.parent is None:
            print color("        Setting Grandparent to: %s" % new_parent_plan, color="red", background="black")
            our_testplans[key].parent.parent = new_parent_plan
    else:
        print color("    Setting Parent to: %s" % new_parent_plan, color="red", background="black")
        our_testplans[key].parent = new_parent_plan



