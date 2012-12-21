nitrate-utils
=============

Some code snippets and utilities facilitating bulk operations on TCMS (Nitrate)

installation
=============
 1. clone [https://github.com/psss/python-nitrate]
 2. run ```make```
 3. fetch any missing things, like ```python-docutils``` or ```rpmbuild```
 4. install it: ```sudo yum install tmp/RPMS/noarch/python-nitrate-0.9-0.fc14.noarch.rpm```
    (or add that ```nitrate``` module to your Python in any other convenient way)
 5. copy ```.nitrate``` to your home and edit ```url``` attribute

utils
=====
check.py
--------
One can use this for verifying the number of test runs created for a particular build.
For instance, suppose we have a tree-style structure as follows:

    Plan A 5552
        |------Plan B TP#8088
        |------Plan C TP#7738
        \------Plan D TP#5709

Plan A does not have any Test Cases not Test Runs, it is just a container. Plans B, C and D have numerous Test Cases and a number of Test Runs created for various Build versions.
Suppose we have two build versions: *PRODUCT8.7.1* and *PRODUCT8.7.2*. Furthermore, there were *n* test runs created for *PRODUCT8.7.1* and we would like to know, whether the *PRODUCT8.7.2* has at least as much test runs as *PRODUCT8.7.1* had. Here we go:

    $ python check.py --plan 5552 --build PRODUCT8.7.1

    TP#8088 - Some test plan covering various interesting features ENABLED
    Runs created for build PRODUCT8.7.1: 1
    TP#7738 - Cthulhu Client backwards compatibility ENABLED
    Runs created for build PRODUCT8.7.1: 0
    TP#5709 - Dark magic connector integration ENABLED
    Runs created for build PRODUCT8.7.1: 14
    For all the test plans, there are 15 runs with build PRODUCT8.7.1

    $ python check.py --plan 5552 --build PRODUCT8.7.2

    TP#8088 - Some test plan covering various interesting features ENABLED
    Runs created for build PRODUCT8.7.2: 5
    TP#7738 - Cthulhu Client backwards compatibility ENABLED
    Runs created for build PRODUCT8.7.2: 0
    TP#5709 - Dark magic connector integration ENABLED
    Runs created for build PRODUCT8.7.2: 14
    For all the test plans, there are 19 runs with build PRODUCT8.7.2

That's it for now. What would you expect from 20 lines of code?