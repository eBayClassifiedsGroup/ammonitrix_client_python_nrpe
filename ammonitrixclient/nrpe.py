#!/usr/bin/env python

import os
import re
import shlex
import subprocess

__author__ = 'rvanleeuwen'
__email__ = 'rvanleeuwen@ebay.com'

class NrpeDirectoryError(Exception):
    pass


class NrpeParseError(Exception):
    pass


class NrpeExecutionError(Exception):
    pass


class Nrpe (object):
    def __init__(self, directory, extension='.cfg'):
        self.nrpe_dir = directory
        self.extension = extension
        self.files = []
        self.commands = dict()

    def read_directory(self):
        self.files = []
        try:
            for file in os.listdir(self.nrpe_dir):
                if file.endswith(self.extension):
                    self.files.append(file)
        except OSError as e:
            raise NrpeDirectoryError(e)

    def parse_files(self):
        """ parse a single nrpe config file

        file usually looks like:
        command[check_ssh]=/usr/lib/nagios/plugins/check_ssh -t 10 localhost

        """
        nrpe_re = re.compile('^.*\[([^\]]*)\]=(.*$)')
        if len(self.files) < 1:
            self.read_directory()
        for file in self.files:
            with open("{}/{}".format(self.nrpe_dir,file), 'r') as f:
                nrpe_conf = f.read()

            match = nrpe_re.match(nrpe_conf)
            if match:
                name = match.group(1)
                command = match.group(2)
                self.commands[name] = command
            else:
                raise NrpeParseError("could not parse:\n{}".format(nrpe_conf))

    def execute_commands(self):
        if len(self.commands) < 1:
            self.parse_files()
        results = {}
        for name, command in self.commands.iteritems():
            resultcode, result = self._execute_single_command(command)

            parsed_result = self.parse_nagiosresult(result)
            results[name] = {'resultcode': resultcode,
                             'result': parsed_result}
        return results


    @staticmethod
    def _execute_single_command(command):
        commandline = shlex.split(command)
        exception_in_cmd = False
        try:
            cmd = subprocess.Popen(commandline,
                                   stdin=None,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
            out, err = cmd.communicate()
            cmd.wait()
            returncode = cmd.returncode
        except OSError as e:
            exception_in_cmd = True
            out = ''
            returncode = 1
        if not exception_in_cmd:
            return returncode, out.rstrip('\r\n')
        printcmdline = ' '.join(commandline)
        raise NrpeExecutionError("Error executing command '{command}': {e}".
                             format(command=printcmdline, e=e))

    def parse_nagiosresult(self, resultline):
        """parse the line(s) returned by nagios

           nagios resultline looks like:

           LDAP OK - 0.001 seconds response |time=0.001362s;;;0.000000
           see https://nagios-plugins.org/doc/guidelines.html#PLUGOUTPUT

           STRING |'label'=value[UOM];[warn];[crit];[min];[max]
        """
        service_status = resultline.split('|')[0]
        results = {'service_status': service_status}
        performance_data = resultline.split('|')[1:]
        for part in performance_data:
            name, value, uom = self.parse_performance_data_part(part)
            #TODO: process multiple
            results['performance_data'] = "{}{}".format(value, uom)
        return results


    @staticmethod
    def parse_performance_data_part(performance_data_part):
        perf_re = re.compile("^'?(?P<name>[^'=]+)'?" +
                             "=(?P<value>[0-9.]+)(?P<uom>[^;]*).*$")
        match = perf_re.match(performance_data_part)
        if match:
            name = match.group('name')
            value = match.group('value')
            uom = match.group('uom')
        else:
            raise NrpeParseError("could not parse:\n{}".
                                 format(performance_data_part))
        return name, value, uom
