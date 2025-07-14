from django import forms
import re

class AddressesForm(forms.Form):
    DHCP_VERSIONS = [
        ('DHCPv4', 'DHCPv4'),
        ('DHCPv6', 'DHCPv6'),
    ]
    dhcp_version = forms.ChoiceField(choices=DHCP_VERSIONS, label='DHCP Version')
    mac_address = forms.CharField(max_length=17, label='MAC Address', help_text='Format: XX:XX:XX:XX:XX:XX (e.g., 00:1A:2B:3C:4D:5E)')

    def clean_mac_address(self):
        mac = self.cleaned_data['mac_address'].upper()
        pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'

        if not re.match(pattern, mac):
            raise forms.ValidationError('Invalid MAC address format. Must be XX:XX:XX:XX:XX:XX')
        return mac

