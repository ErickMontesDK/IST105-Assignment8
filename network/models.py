from django.db import models

class Lease(models.Model):
    DHCP_CHOICES = [
        ('DHCPv4', 'DHCPv4'),
        ('DHCPv6', 'DHCPv6'),
    ]
    mac_address = models.CharField(max_length=17)
    mac_toggle = models.CharField(max_length=17)
    isEvenOrOdd = models.CharField(max_length=4)
    dhcp_version = models.CharField(max_length=6, choices=DHCP_CHOICES)
    assigned_ip = models.CharField(max_length=45) 
    lease_time = models.IntegerField()  
    timestamp = models.DateTimeField()  

    def __str__(self):
        return f"{self.mac_address} - {self.assigned_ip} ({self.dhcp_version})"

    def to_dict(self):
        return {
            "mac_address": self.mac_address,
            "dhcp_version": self.dhcp_version,
            "assigned_ip": self.assigned_ip,
            "lease_time": self.lease_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }