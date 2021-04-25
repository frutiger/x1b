# x1b

A macOS escape route for IP network packets between hosts already on a network.
The program comes in two parts: the part that runs on the gateway and the part
that runs on the client.

Note: almost all of these operations require elevated privilege so you will
have to run them with `sudo` or an elevated shell.

### Roadmap

* Create a VLAN to support multiple clients
* Run a DHCP server to support automatic IP address and DNS server discovery

## Gateway

```
# python3 -m x1b.gateway <client ip>
```

The gateway will serve as the point through which all packets will be routed.
The program performs the following steps:

1. enable packet forwarding
1. enable packet filtering
1. create a NAT rule for each route in the gateway's routing table
1. wait for a `SIGINT` or a `SIGTERM`
1. flush all NAT rules that were
1. disable packet filtering
1. disable packet forwarding

## Client

```
# python3 -m x1b.client <gateway ip> <dns server>
```

The client will modify its routing table to ensure packets flow to the gateway.
The program performs the following steps:

1. add a default route to `<gateway ip>`
1. update the DNS server to `<dns server>`
1. wait for a `SIGINT` or a `SIGTERM`
1. remove `<dns server>` as a DNS server
1. restore the default route

