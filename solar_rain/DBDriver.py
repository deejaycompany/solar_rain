import MySQLdb

import config
from interface import BaseDBDriver
from failed_exception import FailedException
from virtual_machine import VirtualMachine


class DBDriver(BaseDBDriver):
    '''
    Hey there! You can see a class that can provide access to database.
    '''

    def get_vm_by_uuid(self, uuid):
        '''
        The method returns virtual machine object from
        the database by UUID
        '''
        query = "SELECT * FROM vms WHERE uuid = '{0}';".format(uuid)
        result = self._execute_select_query(query)
        try:
            return result[0]
        except:
            return None

    def get_vm_by_name(self, name):
        '''
        The method returns virtual machine object from
        the database by name
        '''
        query = "SELECT * FROM vms WHERE name = '{0}';".format(name)
        result = self._execute_select_query(query)
        try:
            return result[0]
        except:
            return None

    def get_vm_list(self):
        '''
        The method returns all virtual machines from the database
        '''
        query = "SELECT * FROM vms;"
        result = self._execute_select_query(query)
        return result

    def create_vm(self, values={}):
        '''
        This method executes when a machine have been creating.
        '''
        values_string = self._convert_values_to_string_for_create(values)
        query = "INSERT INTO vms VALUES ({0});".format(values_string)
        self._execute_query(query)
        return self.get_vm_by_uuid(values['uuid'])

    def update_vm(self, vm, values={}):
        '''
        This method executes when parameters of virtual machine is changing.
        '''
        v = self._convert_values_to_string_for_update(values)
        query = "UPDATE vms SET {0} WHERE name='{1}';".format(v, vm.name)
        self._execute_query(query)
        return self.get_vm_by_name(vm.name)

    def delete_vm(self, vm):
        '''
        This method executes when user wants to delete a machine
        '''
        query = "DELETE FROM vms WHERE name='{0}';".format(vm.name)
        self._execute_query(query)

    def _convert_values_to_string_for_create(self, values):
        try:
            uuid = self._convert_to_string(values['uuid'])
        except KeyError as e:
            raise FailedException("UUID cannot be null")
        try:
            name = self._convert_to_string(values['name'])
        except KeyError as e:
            raise FailedException("Name cannot be null")
        try:
            vcpu = str(values['vcpu'])
        except KeyError:
            vcpu = "Null"
        try:
            ram = str(values['ram'])
        except KeyError:
            ram = "Null"
        try:
            if values['status'] is True:
                status = "ACTIVE"
            else:
                status = "SHUTDOWN"
            status = self._convert_to_string(status)
        except KeyError:
            status = "Null"
        try:
            libvirt_url = self._convert_to_string(values['libvirt_url'])
        except KeyError:
            libvirt_url = "Null"
        return "{0},{1},{2},{3},{4},{5}".format(uuid, name, vcpu, ram,
                                                status, libvirt_url)

    def _convert_values_to_string_for_update(self, values):
        flag = ""
        try:
            v = values['name']
            name = "name={0}".format(self._convert_to_string(v))
            flag = ","
        except KeyError as e:
            name = ""
        try:
            v = values['vcpu']
            vcpu = "{0} cpu={1}".format(flag, str(v))
            flag = ","
        except KeyError:
            vcpu = ""
        try:
            v = values['ram']
            ram = "{0} ram={1}".format(flag, str(v))
            flag = ","
        except KeyError:
            ram = ""
        try:
            v = values['status']
            if v is True:
                status = "ACTIVE"
            else:
                status = "SHUTDOWN"
            status = "{0} status={1}".format(flag,
                                             self._convert_to_string(status))
            flag = ","
        except KeyError:
            status = ""
        try:
            v = values['libvirt_url']
            url = "{0} libvirt_url={1}".format(flag,
                                               self._convert_to_string(v))
        except KeyError:
            url = ""
        return "{0}{1}{2}{3}{4}".format(name, vcpu, ram, status, url)

    def _convert_to_string(self, value):
        return "'"+str(value)+"'"

    def _execute_query(self, query):
        db = MySQLdb.connect(host=config.DB_CONN_HOST,
                             user=config.DB_CONN_USER,
                             db=config.DB_CONN_DB,
                             charset=config.DB_CONN_CHARSET)
        try:
            cursor = db.cursor()
            print "Query: "+query
            cursor.execute(query)
            db.commit()
            print "The query has been successfully executed!"
        except Exception as e:
            raise FailedException("Query isn't complete. "+str(e[1]))
        finally:
            db.close()

    def _execute_select_query(self, query):
        db = MySQLdb.connect(host=config.DB_CONN_HOST,
                             user=config.DB_CONN_USER,
                             db=config.DB_CONN_DB,
                             charset=config.DB_CONN_CHARSET)
        try:
            cursor = db.cursor()
            print "Query: "+query
            cursor.execute(query)
            data = cursor.fetchall()
            result = []
            for vm in data:
                uuid, name, vcpu, ram, status, libvirt_url = vm
                if str(status) == 'ACTIVE':
                    s = True
                else:
                    s = False
                result.append(VirtualMachine(name, s, uuid, vcpu,
                                             ram, libvirt_url))
            print "The query has been successfully executed!"
            return result
        except Exception as e:
            raise FailedException("Query isn't complete. "+str(e[1]))
        finally:
            db.close()
