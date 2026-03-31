from django import template

register = template.Library()

@register.simple_tag
def define_layers():
    return [
        {'number': 7, 'name': 'Application Layer', 'protocols': 'HTTP, FTP, SMTP, DNS', 'pdu': 'Data', 'opacity': 1.0},
        {'number': 6, 'name': 'Presentation Layer', 'protocols': 'SSL, SSH, IMAP, JPG', 'pdu': 'Data', 'opacity': 0.9},
        {'number': 5, 'name': 'Session Layer', 'protocols': 'NetBIOS, SAP, RPC', 'pdu': 'Data', 'opacity': 0.8},
        {'number': 4, 'name': 'Transport Layer', 'protocols': 'TCP, UDP', 'pdu': 'Segment', 'opacity': 0.7},
        {'number': 3, 'name': 'Network Layer', 'protocols': 'IP, ICMP, IPSec', 'pdu': 'Packet', 'opacity': 0.6},
        {'number': 2, 'name': 'Data Link Layer', 'protocols': 'Ethernet, PPP, Switch', 'pdu': 'Frame', 'opacity': 0.5},
        {'number': 1, 'name': 'Physical Layer', 'protocols': 'Cables, Hubs, Fiber Optics', 'pdu': 'Bits', 'opacity': 0.4},
    ]
