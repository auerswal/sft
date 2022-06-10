#! /usr/bin/awk -f

# vrp_output_to_yaml.awk - Convert Huawei VRP session output to YAML.
# Copyright (C) 2018-2022 Erik Auerswald <auerswal@unix-ag.uni-kl.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# The idea behing this script is to transform the output of a CLI session
# from a Huawei VRP device into a YAML formatted list of dictionaries for
# further processing.  Each dictionary comprises a single command together
# with its output. This YAML formatted data can be read by, e.g., Ansible.
#
# The default output from a simple expect script used to log into a
# Huawei VRP device and execute commands there can be used as input to
# this script.
#
# Since the script relies primarily on the device prompt format, it
# might work with output from devices with a similar prompt format,
# e.g., HPE COMWARE, too.

# /!\ The output of "display ipv6 interface brief" contains lines
#     starting with [IPv6 Address] which looks exactly like a prompt
#     of the system named "IPv6 Address" in immediate system view.
#     Therefore, this script accepts no spaces inside the prompt.

BEGIN {
    progname = "vrp_output_to_yaml.awk"
    found_command = 0
    print "---"
}

# All commands are preceded by the device prompt
# thus this line is not a command invocation.
# Ignore all output before the first command.
! /^(<[^ >]+>|\[[^ \]]+\]) */ {
    if (found_command) {
        # remove all CR characters
        gsub("\r", "")
        # remove VRP line wrap related terminal control sequences
        gsub(" \x1b\\[1D", "")
        # write line to the current command output entry
        print "    " $0
    }
}
# This line has a prompt and might thus contain a command.
/^(<[^ >]+>|\[[^ \]]+\]) */ {
    # a prompt followed by nothing but whitespace is ignored
    if ($0 ~ /^(<[^ >]+>|\[[^ \]]+\]) *\r?$/) next
    # start a new command entry
    found_command = 1
    # remove prompt and whitespace in front of command
    gsub("^(<[^ >]+>|\\[[^ \\]]+\\]) *","")
    # remove all CR characters
    gsub("\r", "")
    # remove VRP line wrap related terminal control sequences (long commands)
    gsub(" \x1b\\[1D", "")
    # if the command ends with a trailing colon, or contains single or double
    #  quotes, it needs to be quoted
    if ($0 ~ /(:$|['"])/) {
        if ($0 !~ /"/ && $0 !~ /'/) {
            $0 = "\"" $0 "\""
        } else if ($0 ~ /"/ && $0 ~ /'/) {
            print progname ": error: cannot quote command '" $0 "'" > "/dev/stderr"
            exit 1
        } else if ($0 ~ /"/) {
            $0 = "'" $0 "'"
        } else {
            $0 = "\"" $0 "\""
        }
    }
    # write beginning of the new command entry
    print "- command: " $0 "\n  output: |\n    ! ENSURE VALID YAML, IGNORE LINE"
}

END {
    fflush("")
    if (!found_command) {
        print progname ": error: found no commands" > "/dev/stderr"
        exit 1
    }
}
