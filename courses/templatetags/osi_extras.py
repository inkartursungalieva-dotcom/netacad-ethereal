import markdown as md
import datetime
from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(md.markdown(text, extensions=['extra', 'codehilite', 'tables']))

@register.filter(name='custom_timesince')
def custom_timesince(value):
    """
    Custom timesince filter with proper translations
    """
    now = timezone.now()
    delta = now - value

    if delta < datetime.timedelta(minutes=1):
        return _("только что")
    elif delta < datetime.timedelta(hours=1):
        minutes = delta.seconds // 60
        return _("%d минут назад") % minutes
    elif delta < datetime.timedelta(days=1):
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        if minutes > 0:
            return _("%d часа %d минут назад") % (hours, minutes)
        else:
            return _("%d часа назад") % hours
    else:
        days = delta.days
        hours = delta.seconds // 3600
        if hours > 0:
            return _("%d дня %d часа назад") % (days, hours)
        else:
            return _("%d дня назад") % days

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
