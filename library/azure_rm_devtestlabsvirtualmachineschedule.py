#!/usr/bin/python
#
# Copyright (c) 2018 Zim Kalinowski, <zikalino@microsoft.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_devtestlabsvirtualmachineschedule
version_added: "2.8"
short_description: Manage Virtual Machine Schedule instance.
description:
    - Create, update and delete instance of Virtual Machine Schedule.

options:
    resource_group:
        description:
            - The name of the resource group.
        required: True
    lab_name:
        description:
            - The name of the lab.
        required: True
    name:
        description:
            - The name of the virtual machine.
        required: True
    name:
        description:
            - The name of the I(schedule).
        required: True
    schedule:
        description:
            - A schedule.
        required: True
        suboptions:
            location:
                description:
                    - The location of the resource.
            status:
                description:
                    - The status of the schedule (i.e. C(enabled), C(disabled)).
                choices:
                    - 'enabled'
                    - 'disabled'
            task_type:
                description:
                    - The task type of the schedule (e.g. LabVmsShutdownTask, LabVmAutoStart).
            weekly_recurrence:
                description:
                    - If the schedule will occur only some days of the week, specify the weekly recurrence.
                suboptions:
                    weekdays:
                        description:
                            - The days of the week for which the schedule is set (e.g. Sunday, Monday, Tuesday, etc.).
                        type: list
                    time:
                        description:
                            - The time of the day the schedule will occur.
            daily_recurrence:
                description:
                    - If the schedule will occur once each day of the week, specify the daily recurrence.
                suboptions:
                    time:
                        description:
                            - The time of day the schedule will occur.
            hourly_recurrence:
                description:
                    - If the schedule will occur multiple times a day, specify the hourly recurrence.
                suboptions:
                    minute:
                        description:
                            - Minutes of the hour the schedule will run.
            time_zone_id:
                description:
                    - The time zone ID (e.g. Pacific Standard time).
            notification_settings:
                description:
                    - Notification settings.
                suboptions:
                    status:
                        description:
                            - If notifications are C(enabled) for this schedule (i.e. C(enabled), C(disabled)).
                        choices:
                            - 'disabled'
                            - 'enabled'
                    time_in_minutes:
                        description:
                            - Time in minutes before event at which notification will be sent.
                    webhook_url:
                        description:
                            - The webhook URL to which the notification will be sent.
            target_resource_id:
                description:
                    - The resource ID to which the schedule belongs
            unique_identifier:
                description:
                    - The unique immutable identifier of a resource (Guid).
    state:
      description:
        - Assert the state of the Virtual Machine Schedule.
        - Use 'present' to create or update an Virtual Machine Schedule and 'absent' to delete it.
      default: present
      choices:
        - absent
        - present

extends_documentation_fragment:
    - azure
    - azure_tags

author:
    - "Zim Kalinowski (@zikalino)"

'''

EXAMPLES = '''
  - name: Create (or update) Virtual Machine Schedule
    azure_rm_devtestlabsvirtualmachineschedule:
      resource_group: NOT FOUND
      lab_name: NOT FOUND
      name: NOT FOUND
      name: NOT FOUND
'''

RETURN = '''
id:
    description:
        - The identifier of the resource.
    returned: always
    type: str
    sample: id
status:
    description:
        - "The status of the schedule (i.e. Enabled, Disabled). Possible values include: 'Enabled', 'Disabled'"
    returned: always
    type: str
    sample: status
'''

import time
from ansible.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from msrest.polling import LROPoller
    from msrestazure.azure_operation import AzureOperationPoller
    from azure.mgmt.devtestlabs import DevTestLabsClient
    from msrest.serialization import Model
except ImportError:
    # This is handled in azure_rm_common
    pass


class Actions:
    NoAction, Create, Update, Delete = range(4)


class AzureRMVirtualMachineSchedules(AzureRMModuleBase):
    """Configuration class for an Azure RM Virtual Machine Schedule resource"""

    def __init__(self):
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            lab_name=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str',
                required=True
            ),
            schedule=dict(
                type='dict',
                required=True
            ),
            state=dict(
                type='str',
                default='present',
                choices=['present', 'absent']
            )
        )

        self.resource_group = None
        self.lab_name = None
        self.name = None
        self.name = None
        self.schedule = dict()

        self.results = dict(changed=False)
        self.mgmt_client = None
        self.state = None
        self.to_do = Actions.NoAction

        super(AzureRMVirtualMachineSchedules, self).__init__(derived_arg_spec=self.module_arg_spec,
                                                             supports_check_mode=True,
                                                             supports_tags=True)

    def exec_module(self, **kwargs):
        """Main module execution method"""

        for key in list(self.module_arg_spec.keys()) + ['tags']:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
            elif kwargs[key] is not None:
                if key == "location":
                    self.schedule["location"] = kwargs[key]
                elif key == "status":
                    self.schedule["status"] = _snake_to_camel(kwargs[key], True)
                elif key == "task_type":
                    self.schedule["task_type"] = kwargs[key]
                elif key == "weekly_recurrence":
                    self.schedule["weekly_recurrence"] = kwargs[key]
                elif key == "daily_recurrence":
                    self.schedule["daily_recurrence"] = kwargs[key]
                elif key == "hourly_recurrence":
                    self.schedule["hourly_recurrence"] = kwargs[key]
                elif key == "time_zone_id":
                    self.schedule["time_zone_id"] = kwargs[key]
                elif key == "notification_settings":
                    ev = kwargs[key]
                    if 'status' in ev:
                        if ev['status'] == 'disabled':
                            ev['status'] = 'Disabled'
                        elif ev['status'] == 'enabled':
                            ev['status'] = 'Enabled'
                    self.schedule["notification_settings"] = ev
                elif key == "target_resource_id":
                    self.schedule["target_resource_id"] = kwargs[key]
                elif key == "unique_identifier":
                    self.schedule["unique_identifier"] = kwargs[key]

        response = None

        self.mgmt_client = self.get_mgmt_svc_client(DevTestLabsClient,
                                                    base_url=self._cloud_environment.endpoints.resource_manager)

        resource_group = self.get_resource_group(self.resource_group)

        old_response = self.get_virtualmachineschedule()

        if not old_response:
            self.log("Virtual Machine Schedule instance doesn't exist")
            if self.state == 'absent':
                self.log("Old instance didn't exist")
            else:
                self.to_do = Actions.Create
        else:
            self.log("Virtual Machine Schedule instance already exists")
            if self.state == 'absent':
                self.to_do = Actions.Delete
            elif self.state == 'present':
                if (not default_compare(self.parameters, old_response, '', {
                       })):
                    self.to_do = Actions.Update

        if (self.to_do == Actions.Create) or (self.to_do == Actions.Update):
            self.log("Need to Create / Update the Virtual Machine Schedule instance")

            if self.check_mode:
                self.results['changed'] = True
                return self.results

            response = self.create_update_virtualmachineschedule()

            self.results['changed'] = True
            self.log("Creation / Update done")
        elif self.to_do == Actions.Delete:
            self.log("Virtual Machine Schedule instance deleted")
            self.results['changed'] = True

            if self.check_mode:
                return self.results

            self.delete_virtualmachineschedule()
            # make sure instance is actually deleted, for some Azure resources, instance is hanging around
            # for some time after deletion -- this should be really fixed in Azure.
            while self.get_virtualmachineschedule():
                time.sleep(20)
        else:
            self.log("Virtual Machine Schedule instance unchanged")
            self.results['changed'] = False
            response = old_response

        if self.state == 'present':
            self.results.update(self.format_item(response))
        return self.results

    def create_update_virtualmachineschedule(self):
        '''
        Creates or updates Virtual Machine Schedule with the specified configuration.

        :return: deserialized Virtual Machine Schedule instance state dictionary
        '''
        self.log("Creating / Updating the Virtual Machine Schedule instance {0}".format(self.name))

        try:
            response = self.mgmt_client.virtual_machine_schedules.create_or_update(resource_group_name=self.resource_group,
                                                                                   lab_name=self.lab_name,
                                                                                   virtual_machine_name=self.name,
                                                                                   name=self.name,
                                                                                   schedule=self.schedule)
            if isinstance(response, LROPoller) or isinstance(response, AzureOperationPoller):
                response = self.get_poller_result(response)

        except CloudError as exc:
            self.log('Error attempting to create the Virtual Machine Schedule instance.')
            self.fail("Error creating the Virtual Machine Schedule instance: {0}".format(str(exc)))
        return response.as_dict()

    def delete_virtualmachineschedule(self):
        '''
        Deletes specified Virtual Machine Schedule instance in the specified subscription and resource group.

        :return: True
        '''
        self.log("Deleting the Virtual Machine Schedule instance {0}".format(self.name))
        try:
            response = self.mgmt_client.virtual_machine_schedules.delete(resource_group_name=self.resource_group,
                                                                         lab_name=self.lab_name,
                                                                         virtual_machine_name=self.name,
                                                                         name=self.name)
        except CloudError as e:
            self.log('Error attempting to delete the Virtual Machine Schedule instance.')
            self.fail("Error deleting the Virtual Machine Schedule instance: {0}".format(str(e)))

        return True

    def get_virtualmachineschedule(self):
        '''
        Gets the properties of the specified Virtual Machine Schedule.

        :return: deserialized Virtual Machine Schedule instance state dictionary
        '''
        self.log("Checking if the Virtual Machine Schedule instance {0} is present".format(self.name))
        found = False
        try:
            response = self.mgmt_client.virtual_machine_schedules.get(resource_group_name=self.resource_group,
                                                                      lab_name=self.lab_name,
                                                                      virtual_machine_name=self.name,
                                                                      name=self.name)
            found = True
            self.log("Response : {0}".format(response))
            self.log("Virtual Machine Schedule instance : {0} found".format(response.name))
        except CloudError as e:
            self.log('Did not find the Virtual Machine Schedule instance.')
        if found is True:
            return response.as_dict()

        return False

    def format_item(self, d):
        d = {
            'id': d.get('id', None),
            'status': d.get('status', None)
        }
        return d


def default_compare(new, old, path):
    if new is None:
        return True
    elif isinstance(new, dict):
        if not isinstance(old, dict):
            return False
        for k in new.keys():
            if not default_compare(new.get(k), old.get(k, None), path + '/' + k):
                return False
        return True
    elif isinstance(new, list):
        if not isinstance(old, list) or len(new) != len(old):
            return False
        if isinstance(old[0], dict):
            key = None
            if 'id' in old[0] and 'id' in new[0]:
                key = 'id'
            elif 'name' in old[0] and 'name' in new[0]:
                key = 'name'
            new = sorted(new, key=lambda x: x.get(key, None))
            old = sorted(old, key=lambda x: x.get(key, None))
        else:
            new = sorted(new)
            old = sorted(old)
        for i in range(len(new)):
            if not default_compare(new[i], old[i], path + '/*'):
                return False
        return True
    else:
        return new == old


def _snake_to_camel(snake, capitalize_first=False):
    if capitalize_first:
        return ''.join(x.capitalize() or '_' for x in snake.split('_'))
    else:
        return snake.split('_')[0] + ''.join(x.capitalize() or '_' for x in snake.split('_')[1:])


def main():
    """Main execution"""
    AzureRMVirtualMachineSchedules()


if __name__ == '__main__':
    main()
