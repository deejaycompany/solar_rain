import uuid

import libvirt
from lxml import etree

from failed_exception import FailedException
from virtual_machine import VirtualMachine
from interface import BaseVMManager
from DBDriver import DBDriver


class VirtualMachineManager(BaseVMManager):
    '''
    This class provides to manage of virtual machines.
    '''

    def __init__(self, libvirt_url):
        self.libvirt_url = libvirt_url
        self.connection = libvirt.open(self.libvirt_url)

    def create(self,
               name,
               vcpu_num,
               ram,
               disk,
               domain_type='qemu',
               emulator='/usr/bin/kvm/'):
        '''
        This method creates a virtual machine with custom parameters.
        Dont give variables Null and ""!
        '''
        try:
            int(vcpu_num)
        except ValueError:
            raise FailedException("Memory must be integer!")
        if int(vcpu_num) < 1:
            raise FailedException("CPU can be positive integer only")
        try:
            int(ram)
        except ValueError:
            raise FailedException("Memory must be integer!")
        if int(ram) < 1:
            raise FailedException("Memory amount can be positive integer "
                                  "only")
        uuid_for_machine = str(uuid.uuid4())
        xmlData = self._generate_xml(name, vcpu_num, ram, disk, domain_type,
                                     emulator, uuid_for_machine)
        try:
            db = DBDriver()
            db.create_vm({'uuid': uuid_for_machine,
                          'name': name,
                          'vcpu': vcpu_num,
                          'ram': ram,
                          'status': False,
                          'libvirt_url': self.libvirt_url})
            self.connection.defineXML(xmlData)
            return VirtualMachine(name, False, uuid_for_machine, vcpu_num, ram,
                                  self.libvirt_url)
        except libvirt.libvirtError as e:
            raise FailedException("Define has failed cause " + e[0])
            return None
        except Exception as e:
            raise FailedException("Unexpected exception cause " + e[0])
            return None

    def _generate_xml(self, name, cpu, ram, disk, domainType, emulator, uuid):
        '''
        This method generate XML-string for creating a virtual machine
        with custom parameters.
        '''
        root = etree.Element("os")
        etree.SubElement(root, "type").text = "hvm"
        subroot = etree.Element("boot", dev='cdrom')
        root.append(subroot)
        sub_el = etree.tostring(root)
        root = etree.Element("domain", type=domainType)
        etree.SubElement(root, "name").text = name
        etree.SubElement(root, "uuid").text = uuid
        etree.SubElement(root, "memory").text = ram
        etree.SubElement(root, "currentMemory").text = ram
        etree.SubElement(root, "vcpu").text = cpu
        root.append(etree.XML(sub_el))
        subroot = etree.Element("clock", offset="utc")
        root.append(subroot)
        etree.SubElement(root, "on_poweroff").text = "destroy"
        etree.SubElement(root, "on_reboot").text = "restart"
        etree.SubElement(root, "on_crash").text = "destroy"
        subroot = etree.Element("devices")
        etree.SubElement(subroot, "emulator").text = emulator
        insubroot = etree.Element("disk", device='disk', type='block')
        insubroot.append(etree.Element("source", dev=disk))
        insubroot.append(etree.Element("target", dev='hda', bus='ide'))
        subroot.append(insubroot)
        subroot.append(etree.Element("input", type='tablet', bus='usb'))
        subroot.append(etree.Element("input", type='mouse', bus='ps2'))
        subroot.append(etree.Element("graphics", type='vnc', port='-1',
                                     listen='127.0.0.1'))
        root.append(subroot)
        return etree.tostring(root)

    def _get_domain_by_name(self, name_of_machine):
        """
        This method returns domain from variable libvirt_url.
        """
        try:
            return self.connection.lookupByName(name_of_machine)
        except libvirt.libvirtError as e:
            raise FailedException("Domain " + name_of_machine + " isnt found!")

    def list_deprecated(self):
        '''
        I guess this method will give users two lists consist of turning
        on and turning off machines.
        '''
        names = self.connection.listDefinedDomains()
        turning_off_list = []
        for name_of_machine in names:
            turning_off_list.append(VirtualMachine(name=name_of_machine,
                                                   status=False))
        turning_on_list = []
        for id in self.connection.listDomainsID():
            dom = self.connection.lookupByID(id)
            infos = dom.info()
            turning_on_list.append(VirtualMachine(name=dom.name(),
                                                  status=True))
        return turning_off_list, turning_on_list

    def list(self):
        db = DBDriver()
        list = db.get_vm_list()
        return list

    def start(self, vm):
        '''
        This method launchs a shutting off machine
        '''
        domain = self._get_domain_by_name(vm.name)
        if domain.isActive():
            raise FailedException("Machine is started already")
        try:
            db = DBDriver()
            vm = db.update_vm(vm, {'status': True})
            domain.create()
        except libvirt.libvirtError as e:
            raise FailedException("Starting has failed cause " + e[0])
        except Exception as e:
            raise FailedException("Unexpected exception cause " + e[0])

    def reboot(self, vm):
        '''
        This method reboots a working machine.
        '''
        domain = self._get_domain_by_name(vm.name)
        if not domain.isActive():
            raise FailedException("Machine isn't active")
        try:
            domain.destroy()
            domain.create()
        except libvirt.libvirtError as e:
            raise FailedException("Rebooting has failed cause " + e[0])
        except Exception as e:
            raise FailedException("Unexpected exception cause " + e[0])

    def shutdown(self, vm):
        '''
        This method shuts down a working machine.
        '''
        domain = self._get_domain_by_name(vm.name)
        if not domain.isActive():
            raise FailedException("Machine isn't active")
        try:
            db = DBDriver()
            vm = db.update_vm(vm, {'status': False})
            domain.destroy()
        except libvirt.libvirtError as e:
            raise FailedException("Shutting down has failed cause " + e[0])
        except Exception as e:
            raise FailedException("Unexpected exception cause " + e[0])

    def delete(self, vm):
        '''
        This method burns with hell fire any virtual machine that
        you give.
        '''
        domain = self._get_domain_by_name(vm.name)
        try:
            db = DBDriver()
            db.delete_vm(vm)
            if domain.isActive():
                domain.destroy()
            domain.undefine()
        except libvirt.libvirtError as e:
            raise FailedException("Deleting has failed cause " + e[0])
        except Exception as e:
            raise FailedException("Unexpected exception cause " + e[0])
