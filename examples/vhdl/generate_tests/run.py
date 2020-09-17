# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2014-2020, Lars Asplund lars.anders.asplund@gmail.com

"""
Generating tests
----------------

Demonstrates generating multiple test runs of the same test bench
with different generic values. Also demonstrates use of ``output_path`` generic
to create test bench output files in location specified by VUnit python runner.
"""

from pathlib import Path
from itertools import product
import sys
import os
sys.path.append(os.path.dirname('/mnt/c/Users/arnfo/Work/vunit/vunit'))
from vunit import VUnit


def make_post_check(data_width, sign):
    """
    Return a check function to verify test case output
    """

    def post_check(output_path):
        """
        This function recives the output_path of the test
        """

        expected = ", ".join([str(data_width), str(sign).lower()]) + "\n"

        output_file = Path(output_path) / "generics.txt"

        print("Post check: %s" % str(output_file))
        with output_file.open("r") as fread:
            got = fread.read()
            if not got == expected:
                print("Content mismatch, got %r expected %r" % (got, expected))
                return False
        return True

    return post_check


def generate_tests(obj, signs, data_widths):
    """
    Generate test by varying the data_width and sign generics
    """

    for sign, data_width in product(signs, data_widths):
        # This configuration name is added as a suffix to the test bench name
        config_name = "data_width=%i,sign=%s" % (data_width, sign)

        # Add the configuration with a post check function to verify the output
        obj.add_config(
            name=config_name,
            generics=dict(data_width=data_width, sign=sign),
            post_check=make_post_check(data_width, sign),
        )


VU = VUnit.from_argv()
LIB = VU.add_library("lib")
LIB.add_source_files(Path(__file__).parent / "test" / "*.vhd")

LIB.set_sim_option('modelsim.vsim_flags', ['-G dur/param_enable=1'])
TB_GENERATED = LIB.test_bench("tb_generated")

# Just set a generic for all configurations within the test bench
TB_GENERATED.set_generic("message", "set-for-entity")

for test in TB_GENERATED.get_tests():
    if test.name == "Test 2":
        # I am trying to achieve two test configurations with following sim_options:
        # test 'cat' : {'modelsim.vsim_flags': ['-G dur/param_enable=1', '-G dur/param_who=cat',
        #                                       '-G dur/param_what=fish', '-G dur/param_eats=YES'], }
        # test 'dog' : {'modelsim.vsim_flags': ['-G dur/param_enable=1', '-G dur/param_who=dog',
        #                                       '-G dur/param_what=fish', '-G dur/param_eats=NO'], }
        #
        # the 'default' configuration is also added to make it easier to see how things work

        # ----------------------------------------------------------------
        # create two configurations with different options
        # note: LIB sim_options are always overwritten, here is no overwrite=False option
        test.add_config(name='cat', sim_options={'modelsim.vsim_flags': ['-G dur/param_who=cat']})
        test.add_config(name='dog', sim_options={'modelsim.vsim_flags': ['-G dur/param_who=dog']})

        # this one preserves default sim_options, and different options could've been
        # added with set_sim_option in each test_case if it got overwrite argument:
        test.add_config(name='default')

        # print test_cases' sim_options
        print('\nSim options after add_configs:')
        for testconfig in [x for x in test._test_case.get_configuration_dicts()[0].values()][1:]:
            print("{} modelsim.vsim_flags : {}".format(testconfig.name, testconfig.sim_options["modelsim.vsim_flags"]))

        # ----------------------------------------------------------------
        # set same sim_option to all test_cases in test
        # this work's okay
        test.set_sim_option('modelsim.vsim_flags', ['-G dur/param_what=fish'], overwrite=False)

        # print test_cases' sim_options
        print('\nSim options after test set_sim_option:')
        for testconfig in [x for x in test._test_case.get_configuration_dicts()[0].values()][1:]:
            print("{} modelsim.vsim_flags : {}".format(testconfig.name, testconfig.sim_options["modelsim.vsim_flags"]))

        # ----------------------------------------------------------------
        # set different optons to differrent test
        for testconfig in [x for x in test._test_case.get_configuration_dicts()[0].values()][1:]:
            # note: Configuration.set_sim_option() does not have overwrite argument
            if testconfig.name == 'cat':
                testconfig.set_sim_option('modelsim.vsim_flags', ['-G dur/param_eats=YES'])
            elif testconfig.name == 'dog':
                testconfig.set_sim_option('modelsim.vsim_flags', ['-G dur/param_eats=NO'])
            else:
                testconfig.set_sim_option('modelsim.vsim_flags', ['-G dur/param_eats=DEFAULT'])

        # print test_cases' sim_options
        print('\nSim options after configuration set_sim_option:')
        for testconfig in [x for x in test._test_case.get_configuration_dicts()[0].values()][1:]:
            print("{} modelsim.vsim_flags : {}".format(testconfig.name, testconfig.sim_options["modelsim.vsim_flags"]))

        print()
    else:
        # Run all other tests with signed/unsigned and data width in range [1,5[
        generate_tests(test, [False, True], range(1, 5))

VU.main()
