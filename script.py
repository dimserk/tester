yaml_config_filename = "tests.yml"
tese_log_filename    = "test_log.txt"

name_key          = "name"
pre_command_key   = "pre_command"
command_key       = "command"
after_command_key = "after_command"
expected_key      = "expected"

fail_string = "\033[41m\033[37m\033[4m Failed \033[0m"
pass_string = "\033[42m\033[37m\033[4m Passed \033[0m"

import yaml
import subprocess

def e_call(command):
    if command == None:
        return None
    else:
        return subprocess.run(command,
            shell=True,
            capture_output=True)

def log(stream, result):
    stream.write("stdout:\n{}\nstderr:\n{}\n".format(
        result.stdout.decode("utf-8") if len(result.stdout) != 0 else "None\n",
        result.stderr.decode("utf-8") if len(result.stderr) != 0 else "None\n"
    ))

def log_test(stream, p_res, res, a_res, test):
    if (p_res != None):
        stream.write("Pre command: {}\n".format(test[pre_command_key]))
        log(stream, p_res)
        stream.write("\n" + "-" * 40 + "\n\n")


    stream.write("Command: {}\n".format(test[command_key]))
    log(stream, res)
    stream.write("return:   {}\nexpected: {}\n".format(
        res.returncode,
        test[expected_key]
    ))

    if (a_res != None):
        stream.write("\n" + "-" * 40 + "\n\n")
        stream.write("After command: {}\n".format(test[after_command_key]))
        log(stream, a_res)

    stream.write("\n" + "=" * 79 + "\n\n")

def validate_tests(tests):
    pass

if __name__ == "__main__":
    with open(yaml_config_filename) as yaml_config:
        tests = yaml.load(yaml_config, Loader=yaml.CLoader)

    validate_tests(tests)

    total_tests = len(tests)
    print(f"Found {total_tests} tests")

    log_file = open("log.txt", "w")

    i = 0
    for test in tests:
        pre_res = None
        res     = None
        aft_res = None
        i += 1

        pre_res = e_call(test[pre_command_key])

        res = e_call(test[command_key])
        test_result = res.returncode

        aft_res = e_call(test[after_command_key])

        log_test(log_file, pre_res, res, aft_res, test)

        # Вывод информации в консоль
        print("-" * 80 + "\n{:>3}/{:<3} {} {}".format(
            i,
            total_tests,
            pass_string if test_result == test[expected_key] else fail_string,
            test[name_key]
        ))

    log_file.close()
