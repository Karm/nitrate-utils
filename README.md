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

**UPDATE:** The current version examines the children Test Plans as well (1 level deep). For instance, if we have a structure like this:

    Plan A 5552
        |------Plan B TP#8088
                    \------Plan BX TP#8089
        |------Plan C TP#7738
        \------Plan D TP#5709

the script will still work. It does not go for grandchildren at the moment. Possible update is a trivial one.
tree_planner.py
---------------
Tree planner takes all *Test Plans* that have **some runs for the given Build specified** and sets the given *Parent Test Plan* for these *Test Plans*. If any of them has a *Parent Test Plan* already and it is not the given *Parent Test Plan*, we set the given *Parent Test Plan* as its *Grandparent Test Plan*.

**Example:**

Picture a situation where we want to generate a structure pretty much like in the aforementioned **check.py** example. At the moment, we have only the Father Test Plan. No Child Test Plans nor Test Runs in it. Nothing.

    Plan A 5552

Furthermore, we have numerous Test Plans like **Plan B TP#8088** (no Test Runs, one Child Test Plan), **Plan BX TP#8089** (some Test Runs for Build *PRODUCT8.7.1*), **Plan C TP#7738** (the same) and **Plan D TP#5709** (the same).

Lets run the script with *--plan 5552* (Plan A 5552) and *--build 1234* (PRODUCT8.7.1):

    $ python tree_planner.py --plan 5552 --build 1234
    
    Test plan ID: 8089 | Test plan name: Plan BX TP#8089
        Parent: Plan B TP#8088
            Grandparent: None
            Setting Grandparent to: Plan A 5552
    Test plan ID: 7738 | Test plan name: Plan C TP#7738
        Parent: None
        Setting Parent to: Plan A 5552
    Test plan ID: 5709 | Test plan name: Plan D TP#5709
        Parent: None
        Setting Parent to: Plan A 5552

results in:

    Plan A 5552
        |------Plan B TP#8088
                    \------Plan BX TP#8089
        |------Plan C TP#7738
        \------Plan D TP#5709

If the Grandparent Test Plan is set already we do nothing:

    Test plan ID: 9999 | Test plan name: TP#9999 - Some test plan
        Parent: TP#9998 - Father to some test plans
            Grandparent: Plan A 5552

If the Parent Test Plan is *Plan A 5552* already we do nothing:

    Test plan ID: 1000 | Test plan name: TP#1000 - Muhehe Plan 
        Parent: Plan A 5552
            Grandparent: None    

That's it.