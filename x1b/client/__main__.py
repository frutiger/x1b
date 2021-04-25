# x1b.client.__main__

import signal
import subprocess
import sys

import netaddr

from x1b import routes

def get_devices():
    output = subprocess.check_output(['networksetup', '-listallhardwareports'],
                                     encoding='ascii')
    lines = output.split('\n')
    result = {}
    for index, line in enumerate(lines):
        if line.startswith('Device'):
            result[line.split(': ')[1]] = lines[index - 1].split(': ')[1]
    return result

def set_dns(service, address):
    subprocess.check_call(['networksetup', '-setdnsservers', service, str(address)])

def clear_dns(service):
    subprocess.check_call(['networksetup', '-setdnsservers', service, 'Empty'])

def main(argv=sys.argv):
    # parse args
    gateway_ip = netaddr.IPAddress(argv[1])
    gateway_dns = netaddr.IPAddress(argv[2])

    devices = get_devices()

    # change default route
    old_gateway = routes.change(routes.k_DEFAULT_ROUTE, gateway_ip)

    # update dns
    for route in routes.get_all():
        set_dns(devices[route.iface], gateway_dns)

    signal.sigwait([signal.SIGINT, signal.SIGTERM])

    # reset dns
    for route in routes.get_all():
        clear_dns(devices[route.iface])

    # restore default route
    if old_gateway != None:
        routes.change(routes.k_DEFAULT_ROUTE, old_gateway)

if __name__ == '__main__':
    main()

