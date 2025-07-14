from datetime import datetime
import time
from django.shortcuts import render
from django.utils import timezone

from network.models import Lease
from .forms import AddressesForm

# Lease time default(seconds)
LEASE_TIME_DEFAULT = 3600
IPV4_COUNTER = 1


def generate_lease(dhcp_version, mac, mac_toggle, ip, isEvenOrOdd, lease_time=LEASE_TIME_DEFAULT):
    lease_obj = Lease.objects.create(
        mac_address=mac,
        mac_toggle = mac_toggle,
        isEvenOrOdd = isEvenOrOdd,
        dhcp_version=dhcp_version,
        assigned_ip=ip,
        lease_time=lease_time,
        timestamp=timezone.now()
    )
    return lease_obj.to_dict()

def check_lease(mac):
    existing_lease = Lease.objects.filter(mac_address=mac).order_by('-timestamp').first()
    
    if existing_lease:
        lease = existing_lease.to_dict()
        lease_start = datetime.fromisoformat(lease['timestamp'])
        lease_start = lease_start.timestamp()

        
        if time.time() - lease_start < lease['lease_time']:
            return lease
        else:
            print("Expired lease")
    return None


def generate_ipv4():
    for i in range(1, 255):
        ip_address = f"192.168.1.{i}"
        lease = Lease.objects.filter(assigned_ip=ip_address).order_by('-timestamp').first()
        if lease:  
            lease_start = lease.timestamp
            if isinstance(lease_start, str):
                lease_start = datetime.fromisoformat(lease_start)
            lease_start = lease_start.timestamp()
            if time.time() - lease_start < lease.lease_time:
                continue  
            
        return ip_address
    return None

def generate_ipv6(mac_address):
    mac_clean = mac_address.replace(':', '')
    mac_bytes = [int(mac_clean[i:i+2], 16) for i in range(0, 12, 2)]
    
    mac_bytes[0] ^= 0x02
    eui64_bytes = mac_bytes[:3] + [0xFF, 0xFE] + mac_bytes[3:]
    
    groups = []
    for i in range(0, 8, 2):
        group = f"{eui64_bytes[i]:02x}{eui64_bytes[i+1]:02x}"
        groups.append(group)
    
    eui64 = ':'.join(groups)
    
    ipv6 = f"2001:db8::{eui64}"
    return ipv6

def bitwise_mac(mac_address):
    mac_clean = mac_address.replace(':', '')
    mac_bytes = [int(mac_clean[i:i+2], 16) for i in range(0, 12, 2)]
    
    mac_bytes[0] ^= 0x02
    total = sum(mac_bytes)
    even_odd = 'even' if (total & 1) == 0 else 'odd'
    eui64_bytes = mac_bytes[:3] + [0xFF, 0xFE] + mac_bytes[3:]
    
    groups = []
    for i in range(0, 8, 2):
        group = f"{eui64_bytes[i]:02x}{eui64_bytes[i+1]:02x}"
        groups.append(group)
    
    mac_toggled = ':'.join(groups)
    return even_odd, mac_toggled

def lease_address(request):
    result = None
    if request.method == 'POST':
        form = AddressesForm(request.POST)
        
        if form.is_valid():
            dhcp_version = form.cleaned_data['dhcp_version']
            mac = form.cleaned_data['mac_address']
            
            
            existing_lease = check_lease(mac)
            
            if existing_lease:
                result = existing_lease
            else:
                even_or_odd, mac_toggled = bitwise_mac(mac)
                ip = generate_ipv4() if dhcp_version == 'DHCPv4' else generate_ipv6(mac_toggled)
                result = generate_lease(dhcp_version, mac, mac_toggled, ip, even_or_odd)
                
            return render(request, 'result.html', {'form': form, 'result':result})
        
            
    else:
        form = AddressesForm()
    return render(request, 'index.html', {'form': form})


def list_leases(request):
    leases = Lease.objects.all().order_by('-timestamp')
    return render(request, 'leases.html', {'leases': leases})
    