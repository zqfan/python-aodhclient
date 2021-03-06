#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_serialization import jsonutils

from aodhclient.v2.alarm_cli import ALARM_TYPES
from aodhclient.v2 import base


class AlarmManager(base.Manager):

    url = "v2/alarms"

    @staticmethod
    def _filtersdict_to_url(filters):
        urls = []
        for k, v in sorted(filters.items()):
            url = "q.field=%s&q.op=eq&q.value=%s" % (k, v)
            urls.append(url)
        return '&'.join(urls)

    def list(self, query=None, filters=None):
        """List alarms.

        :param query: A json format complex query expression, like this:
                      '{"=":{"type":"threshold"}}', this expression is used to
                      query all the threshold type alarms.
        :type query: json
        :param filters: A dict includes filters parameters, for example,
                        {'type': 'threshold', 'severity': 'low'} represent
                        filters to query alarms with type='threshold' and
                        severity='low'.
        :type filters: dict
        """
        if query:
            query = {'filter': query}
            url = "v2/query/alarms"
            return self._post(url,
                              headers={'Content-Type': "application/json"},
                              data=jsonutils.dumps(query)).json()
        else:
            url = (self.url + '?' + self._filtersdict_to_url(filters) if
                   filters else self.url)
            return self._get(url).json()

    def get(self, alarm_id):
        """Get an alarm

        :param alarm_id: ID of the alarm
        :type alarm_id: str
        """
        return self._get(self.url + '/' + alarm_id).json()

    @staticmethod
    def _clean_rules(alarm_type, alarm):
        for rule in ALARM_TYPES:
            if rule != alarm_type:
                alarm.pop('%s_rule' % rule, None)

    def create(self, alarm):
        """Create an alarm

        :param alarm: the alarm
        :type alarm: dict
        """
        self._clean_rules(alarm['type'], alarm)
        return self._post(
            self.url, headers={'Content-Type': "application/json"},
            data=jsonutils.dumps(alarm)).json()

    def update(self, alarm_id, alarm_update):
        """Update an alarm

        :param alarm_id: ID of the alarm
        :type alarm_id: str
        :param attributes: Attributes of the alarm
        :type attributes: dict
        """
        alarm = self._get(self.url + '/' + alarm_id).json()
        self._clean_rules(alarm['type'], alarm_update)

        if 'threshold_rule' in alarm_update:
            alarm['threshold_rule'].update(alarm_update.get('threshold_rule'))
            alarm_update.pop('threshold_rule')
        elif 'event_rule' in alarm_update:
            alarm['event_rule'].update(alarm_update.get('event_rule'))
            alarm_update.pop('event_rule')
        elif 'gnocchi_resources_threshold_rule' in alarm_update:
            alarm['gnocchi_resources_threshold_rule'].update(
                alarm_update.get('gnocchi_resources_threshold_rule'))
            alarm_update.pop('gnocchi_resources_threshold_rule')
        elif 'gnocchi_aggregation_by_metrics_threshold_rule' in alarm_update:
            alarm['gnocchi_aggregation_by_metrics_threshold_rule'].update(
                alarm_update.get(
                    'gnocchi_aggregation_by_metrics_threshold_rule'))
            alarm_update.pop('gnocchi_aggregation_by_metrics_threshold_rule')
        elif 'gnocchi_aggregation_by_resources_threshold_rule' in alarm_update:
            alarm['gnocchi_aggregation_by_resources_threshold_rule'].update(
                alarm_update.get(
                    'gnocchi_aggregation_by_resources_threshold_rule'))
            alarm_update.pop(
                'gnocchi_aggregation_by_resources_threshold_rule')
        elif 'composite_rule' in alarm_update:
            if alarm_update['composite_rule']:
                alarm['composite_rule'] = alarm_update['composite_rule']
            alarm_update.pop('composite_rule')

        alarm.update(alarm_update)
        return self._put(
            self.url + '/' + alarm_id,
            headers={'Content-Type': "application/json"},
            data=jsonutils.dumps(alarm)).json()

    def delete(self, alarm_id):
        """Delete an alarm

        :param alarm_id: ID of the alarm
        :type alarm_id: str
        """
        self._delete(self.url + '/' + alarm_id)
