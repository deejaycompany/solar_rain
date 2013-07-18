#! /usr/bin/env python
import argparse
import os
import uuid

from solar_rain.failed_exception import FailedException
from solar_rain.virtual_machine_manager import VirtualMachineManager
from solar_rain.virtual_machine import VirtualMachine


def checkOutDefaultValues(n, c, m, d, t, e):
    '''
    This method checks variables for Null and empty values and return default
    instead.
    '''
    if n is None or n == "":
        n = "defaultName"
    if c is None or c == "":
        c = "1"
    if m is None or m == "":
        m = "524288"
    if d is None or d == "":
        d = "/dev/sr0"
    if t is None or t == "":
        t = "qemu"
    if e is None or e == "":
        e = "/usr/bin/kvm"
    return n, c, m, d, t, e


def menu(manager, greetMsg):
    '''
    There's some code for display and generate menu information.
    '''
    os.system("clear")
    print "Good 2 c u!"
    list = manager.list()
    print convertListToString(list)
    print "Available actions:"
    return raw_input(greetMsg)


def convertVMListToString(notworking, working):
    '''
    This code turns information from list into usable text form.
    DEPRECATED!
    uses informaion from libvirt
    '''
    result = "Don't working: "
    for item in notworking:
        result = result + item.name + ", "
    result = result + "\nWorking: "
    for item in working:
        result = result + item.name + ", "
    return result


def convertListToString(list):
    '''
    This code turns information from list into usable text form.
    RECOMENDED!
    uses information from database
    '''
    result = "Machines:\n"
    for item in list:
        if item.status is True:
            status = "Working."
        else:
            status = "Isn't working."
        s = "Machine {0}. UUID is {1}, memory = {2}, CPUs = {3}. {4}\n"
        s = s.format(item.name, item.uuid, str(item.ram), str(item.vcpu_num),
                     status)
        result = result + s
    return result


def tryToGetCmdArguments(manager):
    '''
    This code tries to parse command line arguments and do something with it.
    If command line arguments don't exist program show users the main menu.
    If command line arguments exist program do something and return user to
    system command line.
    '''
    progName = "Virtual Machine Manager by Deejay"
    progDescription = ("This simple program just give you a chance to create "
                       "and manage your virtual machines by QEMU :D) Author "
                       "doesn't have responsibility for "
                       "this program will work. All right reserved! =)")
    progEpilog = "Have a good one!"
    theBloodyParser = argparse.ArgumentParser(prog=progName,
                                              description=progDescription,
                                              epilog=progEpilog)
    theBloodyParser.add_argument("-do", help="Actions. Variants: create, "
                                 "info, start, shutdown, delete, "
                                 "reboot")
    theBloodyParser.add_argument("-t", help="domain type")
    theBloodyParser.add_argument("-n", help="name of machine")
    theBloodyParser.add_argument("-m", help="amount of memory")
    theBloodyParser.add_argument("-c", help="amount of CPUs")
    theBloodyParser.add_argument("-e", help="emulator location")
    theBloodyParser.add_argument("-d", help="disk location")
    theBloodyParser.add_argument("-id", help="identificator")
    arguments = theBloodyParser.parse_args()
    if arguments.do is None:
        return 0
    if arguments.do == "create":
        try:
            n, c, m, d, t, e = checkOutDefaultValues(arguments.n,
                                                     arguments.c,
                                                     arguments.m,
                                                     arguments.d,
                                                     arguments.t,
                                                     arguments.e)
            manager.create(n, c, m, d, t, e)
        except FailedException as e:
            print "Fuck it! " + e.message
        else:
            print "Fuck yeah!"
    elif arguments.do == "start":
        try:
            if arguments.n is None or arguments.n == "":
                raise FailedException("Did you forget -n attribute?")
            manager.start(VirtualMachine(name=arguments.n,
                                         libvirt_url=manager.libvirt_url))
        except FailedException as e:
            print "Fuck it! " + e.message
        else:
            print "Fuck yeah!"
    elif arguments.do == "shutdown":
        try:
            if arguments.n is None or arguments.n == "":
                raise FailedException("Did you forget -n attribute?")
            vm = VirtualMachine(name=arguments.n,
                                libvirt_url=manager.libvirt_url)
            manager.shutdown(vm)
        except FailedException as e:
            print "Fuck it! " + e.message
        else:
            print "Fuck yeah!"
    elif arguments.do == "delete":
        try:
            if arguments.n is None or arguments.n == "":
                raise FailedException("Did you forget -n attribute?")
            manager.delete(VirtualMachine(name=arguments.n,
                                          libvirt_url=manager.libvirt_url))
        except FailedException as e:
            print "Fuck it! " + e.message
        else:
            print "Fuck yeah!"
    elif arguments.do == "reboot":
        try:
            if arguments.n is None or arguments.n == "":
                raise FailedException("Did you forget -n attribute?")
            manager.reboot(VirtualMachine(name=arguments.n,
                                          libvirt_url=manager.libvirt_url))
        except FailedException as e:
            print "Fuck it! " + e.message
        else:
            print "Fuck yeah!"
    elif arguments.do == "infodeprecated":
        turning_off_list, turning_on_list = manager.list_deprecated()
        print convertVMListToString(turning_off_list, turning_on_list)
    elif arguments.do == "info":
        list = manager.list()
        print convertListToString(list)
    else:
        print("Incorrect -do argument! Program requres create, start,"
              " shutdown, info, reboot or delete")
    return 1


def main():
    '''
    main function. I suppose it doesn't requre comments.
    '''
    manager = VirtualMachineManager("qemu:///system")
    if tryToGetCmdArguments(manager) == 1:
        return
    a = 0
    while a != "0":
        a = menu(manager, "1) Create\n2) Start\n3) Shutdown\n4) Delete\n"
                 "5) Reboot\n0) Run away\n")
        if a == "1":
            try:
                n = raw_input("Name: ")
                c = raw_input("CPUs: ")
                m = raw_input("Memory: ")
                t = raw_input("Domain type: ")
                e = raw_input("Emulator location: ")
                d = raw_input("Disk location: ")
                n, c, m, d, t, e = checkOutDefaultValues(n, c, m, d, t, e)
                manager.create(n, c, m, d, t, e)
            except FailedException as e:
                print "Fuck it! " + e.message
            else:
                print "Fuck yeah!"
        elif a == "2":
            try:
                n = raw_input("Name: ")
                if n is None or n == "":
                    raise FailedException("You input incorrect name!")
                vm = VirtualMachine(name=n,
                                    libvirt_url=manager.libvirt_url)
                manager.start(vm)
            except FailedException as e:
                print "Fuck it! " + e.message
            else:
                print "Fuck yeah!"
        elif a == "3":
            try:
                n = raw_input("Name: ")
                if n is None or n == "":
                    raise FailedException("You input incorrect name!")
                vm = VirtualMachine(name=n,
                                    libvirt_url=manager.libvirt_url)
                manager.shutdown(vm)
            except FailedException as e:
                print "Fuck it! " + e.message
            else:
                print "Fuck yeah!"
        elif a == "4":
            try:
                n = raw_input("Name: ")
                if n is None or n == "":
                    raise FailedException("You input incorrect name!")
                vm = VirtualMachine(name=n,
                                    libvirt_url=manager.libvirt_url)
                manager.delete(vm)
            except FailedException as e:
                print "Fuck it! " + e.message
            else:
                print "Fuck yeah!"
        elif a == "5":
            try:
                n = raw_input("Name: ")
                if n is None or n == "":
                    raise FailedException("You input incorrect name!")
                vm = VirtualMachine(name=n,
                                    libvirt_url=manager.libvirt_url)
                manager.reboot(vm)
            except FailedException as e:
                print "Fuck it! " + e.message
            else:
                print "Fuck yeah!"
        raw_input("Press ENTER to continue")

if __name__ == "__main__":
    '''
    It needs.
    '''
    main()
