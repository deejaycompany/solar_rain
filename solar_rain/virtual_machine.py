import libvirt

from interface import BaseVirtualMachine


class VirtualMachine(BaseVirtualMachine):
    """Represents virtual machine."""

    name = None
    uuid = None
    vcpu_num = None
    ram = None
    libvirt_url = None
    status = None

    def __init__(self, name, status=None, uuid=None, vcpu_num=None, ram=None,
                 libvirt_url=None):
        self.name = name
        self.uuid = uuid
        self.vcpu_num = vcpu_num
        self.ram = ram
        self.libvirt_url = libvirt_url
        self.connection = libvirt.open(self.libvirt_url)
        self.status = status
