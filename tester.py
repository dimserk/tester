"""
    Module for testing console programs
    V 1.1
"""

import os
import sys
import argparse
import subprocess
from math import ceil
import yaml

# Ключевые строки словаря с тестом
NAME_KEY          = "name"
PRE_COMMAND_KEY   = "pre_command"
COMMAND_KEY       = "command"
AFTER_COMMAND_KEY = "after_command"
EXPECTED_KEY      = "expected"

FAIL_STRING = "\033[31m Failed \033[0m"
PASS_STRING = "\033[32m Passed \033[0m"

def validate_tests(raw_tests):
    """
        Function for validating tests, comming from file
    """

    valid_tests = []

    for raw_test in raw_tests:
        # Обязательные параметры теста
        if EXPECTED_KEY not in raw_test:
            continue

        if COMMAND_KEY not in raw_test:
            continue

        # Необязательные параметры теста
        if PRE_COMMAND_KEY not in raw_test:
            raw_test[PRE_COMMAND_KEY] = None

        if AFTER_COMMAND_KEY not in raw_test:
            raw_test[AFTER_COMMAND_KEY] = None

        if NAME_KEY not in raw_test:
            raw_test[NAME_KEY] = ''

        valid_tests.append(raw_test)

    return valid_tests

def e_call(command):
    """
        Function for executing shell command
    """

    if command is not None:
        return None

    return subprocess.run(command,
        shell=True,
        check=False,
        capture_output=True)

def log(stream, result):
    """
        Function for writing command output to stream
    """

    stream.write("{}".format(result.stdout.decode("utf-8")
        if len(result.stdout) != 0 else "\n"))

    if len(result.stderr) != 0:
        stream.write("stderr:\n{}\n".format(result.stderr.decode("utf-8")))

def log_test(stream, p_res, c_res, a_res, test_case):
    """
        Function for writing test results to stream
    """

    if p_res is not None:
        stream.write("Pre command: {}\n".format(test_case[PRE_COMMAND_KEY]))
        log(stream, p_res)
        stream.write("\n" + "=" * 5 + ">\n\n")


    stream.write("Command: {}\n".format(test_case[COMMAND_KEY]))
    log(stream, c_res)
    stream.write("return:   {}\nexpected: {}\n".format(
        c_res.returncode,
        test_case[EXPECTED_KEY]
    ))

    if a_res is not None:
        stream.write("\n" + "=" * 5 + ">\n\n")
        stream.write("After command: {}\n".format(test_case[AFTER_COMMAND_KEY]))
        log(stream, a_res)

    stream.write("\n" + "=" * 79 + "\n\n")

if __name__ == "__main__":
    # Определение CLI
    argparser = argparse.ArgumentParser(description='Util for testing \
        console programs')
    argparser.add_argument('--no-log', '-n', help='turn off logging',
        action='store_true')
    argparser.add_argument('--minimum', '-m', help='minimaze console output',
        action='store_true', default=False)
    argparser.add_argument('--test-dir', '-t',
        help='point to tests dir [default .]', default='.')
    args = argparser.parse_args()

    # Получение всех файлов, находящихся в одной директории с этим файлом
    os.chdir(os.path.split(os.path.abspath(sys.argv[0]))[0])
    try:
        all_files = os.listdir(args.test_dir)
    except FileNotFoundError:
        print(f"Can not look for tests at {args.test_dir}")
        sys.exit(1)

    # Поиск YAML файлов с тестами
    test_files = [file for file in all_files
        if file.find(".yml") != -1 or file.find(".yaml") != -1]

    if test_files.count == 0:
        print("No test groups found")
        sys.exit(1)

    # Обработка тестов
    for test_file in test_files:
        with open(test_file) as yaml_config:
            tests = yaml.load(yaml_config, Loader=yaml.CLoader)

        test_group_name = os.path.splitext(os.path.basename(test_file))[0]
        print(f"Test group: {test_group_name}")

        tests = validate_tests(tests)
        if len(tests) == 0:
            continue

        print(f"Found {len(tests)} tests")

        test_log_name = f"{test_group_name}_log.txt"
        if not args.no_log and os.path.exists(test_log_name):
            os.remove(test_log_name)

        passed_tests = 0
        for i, test in enumerate(tests, start=1):
            pre_res = e_call(test[PRE_COMMAND_KEY])
            res     = e_call(test[COMMAND_KEY])
            aft_res = e_call(test[AFTER_COMMAND_KEY])

            if res.returncode == test[EXPECTED_KEY]:
                RESULT_STRING = PASS_STRING
                passed_tests += 1
            else:
                RESULT_STRING = FAIL_STRING

            if not args.minimum:
                print("{:>3}/{:<3} {} {}".format(
                    i,
                    len(tests),
                    RESULT_STRING,
                    test[NAME_KEY]
                ))

            if not args.no_log:
                with open(test_log_name, "a") as log_file:
                    log_test(log_file, pre_res, res, aft_res, test)

        print(f"{ceil(passed_tests / len(tests) * 100)}% passed", end="\n\n")
