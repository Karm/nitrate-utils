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

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="check.py --plan PLAN --build BUILD [options]")
    parser.add_option("--plan", dest="plan", type="int", help="test plan id")
    parser.add_option("--build", dest="build", type="int", help="build id")
    options = parser.parse_args()[0]

our_testplans = {}
try:
    new_parent_plan = TestPlan(options.plan)
except xmlrpclib.ProtocolError, err:
    logerror(err)
    new_parent_plan = TestPlan(options.plan)

try:
    testruns = TestRun.search(build=options.build)
except xmlrpclib.ProtocolError, err:
    logerror(err)
    testruns = TestRun.search(build=options.build)

for testrun in testruns:
    try:
        our_testplans[testrun.testplan.id] = testrun.testplan
    except xmlrpclib.ProtocolError, err:
        logerror(err)
        our_testplans[testrun.testplan.id] = testrun.testplan
print color("--------------------------------TEST PLANS---------------------------------", color="green", background="black")
for key in our_testplans.keys():
    
    try:
        test_plan_name = our_testplans[key].name
    except xmlrpclib.ProtocolError, err:
        logerror(err)
        test_plan_name = our_testplans[key].name
    print "Test plan ID: %d | Test plan name: %s" % (key, test_plan_name)

    test_plan_parent_name = our_testplans[key].parent
    if test_plan_parent_name is not None:
        try:
            test_plan_parent_name = test_plan_parent_name.name
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            test_plan_parent_name = test_plan_parent_name.name
    print "    Parent: %s" % test_plan_parent_name
    
    if our_testplans[key].parent is not None:
    
        test_plan_grandparent_name = our_testplans[key].parent.parent
        if test_plan_grandparent_name is not None:
            try:
                test_plan_grandparent_name = test_plan_grandparent_name.name
            except xmlrpclib.ProtocolError, err:
                logerror(err)
                test_plan_grandparent_name = test_plan_grandparent_name.name
        print "        Grandparent: %s" % test_plan_grandparent_name
    
        if our_testplans[key].parent.id != new_parent_plan.id and our_testplans[key].parent.parent is None:
            print color("        Setting Grandparent to: %s" % new_parent_plan, color="yellow", background="black")
            try:
                our_testplans[key].parent.parent = new_parent_plan
            except xmlrpclib.ProtocolError, err:
                logerror(err)
                our_testplans[key].parent.parent = new_parent_plan
    else:
        print color("    Setting Parent to: %s" % new_parent_plan, color="yellow", background="black")
        try:
            our_testplans[key].parent = new_parent_plan
        except xmlrpclib.ProtocolError, err:
            logerror(err)
            our_testplans[key].parent = new_parent_plan
print color("We are done.", color="green", background="black")