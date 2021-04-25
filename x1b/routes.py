# x1b.util.routes

from dataclasses import dataclass
import subprocess

import netaddr

@dataclass
class Route:
    iface: str
    destination: netaddr.IPNetwork
    gateway: netaddr.IPAddress

k_DEFAULT_ROUTE = netaddr.IPNetwork('0.0.0.0/0')

def get_all():
    output = subprocess.check_output(['netstat', '-rn', '-f', 'inet'],
                                     encoding='ascii')
    for line in output.split('\n')[4:-1]:
        destination, gateway, _, iface = line.split(maxsplit=3)

        if destination == 'default':
            destination = k_DEFAULT_ROUTE
        else:
            destination = netaddr.IPNetwork(destination)

        try:
            gateway = netaddr.IPAddress(gateway)
        except netaddr.core.AddrFormatError:
            continue

        iface = iface.split()[0]
        if iface.startswith('lo'):
            continue

        yield Route(iface, destination, gateway)

def change(destination, gateway):
    routes = get_all()
    for route in routes:
        if route.destination == destination:
            old_destination = route.gateway
            subprocess.check_call(['route', 'change', str(destination.ip), str(gateway)])
            return old_destination
    subprocess.check_call(['route', 'add', str(destination.ip), str(gateway)])
    return None

