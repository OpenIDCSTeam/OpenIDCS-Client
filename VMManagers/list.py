#!/usr/bin/env python3

import sys
import argparse
import logging

try:
    import pyvix
except ImportError:
    sys.stderr.write('Missing pyvix module\n')
    sys.exit(-1)

print('Connecting...', end=' ')
host = pyvix.connect()
print('OK')

print('Host Version:', host.property(pyvix.PROPERTY_HOST_SOFTWARE_VERSION))

vms = host.running()
vms.sort()
if not vms:
    print('No running virtual machines')
else:
    print('Running virtual machines:')
    for vmname in vms:
        vm = host.open(vmname)
        print(' *', vm.property(pyvix.PROPERTY_VM_VMX_PATHNAME)) # same as vmname
        print(' Name: ', vm.property(pyvix.PROPERTY_VM_NAME))
        print(' Guest:', vm.property(pyvix.PROPERTY_VM_GUESTOS))
        print(' CPUs:', vm.property(pyvix.PROPERTY_VM_NUM_VCPUS), ' Memory:', vm.property(pyvix.PROPERTY_VM_MEMORY_SIZE), 'MB')
        print(' Running: ', vm.property(pyvix.PROPERTY_VM_IS_RUNNING))
        print(' VM Tools:', vm.property(pyvix.PROPERTY_VM_TOOLS_STATE))
        #print('PROPERTY_VM_SUPPORTED_FEATURES:', vm.property(pyvix.PROPERTY_VM_SUPPORTED_FEATURES))

        print('Waiting for 5 seconds...')
        try:
            vm.waitfortools(5)
        except pyvix.error:
            print('Tools are not available')

        # sometimes the powerstate has extra undocumented bits turned on
        powerstate = vm.property(pyvix.PROPERTY_VM_POWER_STATE)
        if powerstate & pyvix.POWERSTATE_POWERING_OFF:
            print('POWERSTATE_POWERING_OFF')
        if powerstate & pyvix.POWERSTATE_POWERED_OFF:
            print('POWERSTATE_POWERED_OFF')
        if powerstate & pyvix.POWERSTATE_POWERING_ON:
            print('POWERSTATE_POWERING_ON')
        if powerstate & pyvix.POWERSTATE_POWERED_ON:
            print('POWERSTATE_POWERED_ON')
        if powerstate & pyvix.POWERSTATE_SUSPENDING:
            print('POWERSTATE_SUSPENDING')
        if powerstate & pyvix.POWERSTATE_SUSPENDED:
            print('POWERSTATE_SUSPENDED')
        if powerstate & pyvix.POWERSTATE_TOOLS_RUNNING:
            print('POWERSTATE_TOOLS_RUNNING')
        if powerstate & pyvix.POWERSTATE_RESETTING:
            print('POWERSTATE_RESETTING')
        if powerstate & pyvix.POWERSTATE_BLOCKED_ON_MSG:
            print('POWERSTATE_BLOCKED_ON_MSG')
        if powerstate & pyvix.POWERSTATE_PAUSED:
            print('POWERSTATE_PAUSED')
        if powerstate & pyvix.POWERSTATE_RESUMING:
            print('POWERSTATE_RESUMING')
        print()
        vm.close()

if len(sys.argv) > 1:
    vm = host.open(sys.argv[1])
    vm.waitfortools()
    vm.login('user', 'password', pyvix.LOGIN_IN_GUEST_REQUIRE_INTERACTIVE_ENVIRONMENT)
    vm.run('C:\\windows\\notepad.exe', '', False)
    tasklist = vm.tasklist()
    for task in tasklist:
        print('%d: %s: %s' % task)
    vm.logout()
    vm.close()

host.disconnect()

