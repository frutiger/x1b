# x1b.gateway.__main__

from dataclasses import dataclass
import subprocess
import signal
import sys
import tempfile

import netaddr

from x1b import routes

# usage: gateway
# 1. enable packet filtering
# 2. for each route/change in this host's table, add a NAT route:
#      nat pass on <parent> inet from <net> to <dest> -> <addr on parent>
# TODO:
# 3. monitor for route changes

@dataclass
class Interface:
    iface: str
    address: netaddr.IPAddress
    network: netaddr.IPNetwork

def get_ifaces():
    output = subprocess.check_output(['ifconfig', '-a', 'inet'],
                                     encoding='ascii')
    lines = output.split('\n')[::-1]
    for index, line in enumerate(lines):
        if line.lstrip().startswith('inet'):
            items = line.split()
            address = netaddr.IPAddress(items[1])
            network = netaddr.IPNetwork(items[1])
            if 'netmask' in items:
                network.netmask = items[items.index('netmask') + 1]
            i = index + 1
            while i < len(lines):
                if not lines[i][0].isspace():
                    yield Interface(lines[i].split(':')[0], address, network)
                    break
                i += 1

def clear_nat():
    subprocess.check_call(['pfctl', '-F', 'nat'])
    subprocess.call(['pfctl', '-d'])

def set_nat(client_ip, client_iface, ifaces, routes):
    with tempfile.NamedTemporaryFile() as f:
        for route in routes:
            for iface in ifaces:
                if route.gateway in iface.network:
                    rule = f'nat pass on {iface.iface} from {client_ip} to {route.destination} -> {iface.address}\n'
                    rule = rule.encode('ascii')
                    f.write(rule)
                    f.flush()
                    break
            else:
                raise RuntimeError(f'Could not find interface for {route.gateway}')
        subprocess.call(['pfctl', '-e'])
        subprocess.check_call(['pfctl', '-f', f.name])

def main(argv=sys.argv):
    # parse args
    client_ip = netaddr.IPAddress(argv[1])
    ifaces = list(get_ifaces())
    for iface in ifaces:
        if client_ip in iface.network:
            client_iface = iface
            break
    else:
        raise RuntimeError(f'Could not find interface for {client_ip}')

    # get routes
    all_routes = routes.get_all()

    # enable packet filtering
    subprocess.call(['sysctl', 'net.inet.ip.forwarding=1'])

    # append nat rule for each route
    set_nat(client_ip, client_iface, ifaces, all_routes)

    signal.sigwait([signal.SIGINT, signal.SIGTERM])

    # clear nat rules
    clear_nat()

    # disable packet filtering
    subprocess.call(['sysctl', 'net.inet.ip.forwarding=0'])

if __name__ == '__main__':
    main()

