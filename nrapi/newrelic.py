import redis
import requests
import json
from werkzeug.contrib.cache import SimpleCache, RedisCache
from flask import current_app as app
from nr_app import App
from nr_label import Label
from nr_term import Term
from nr_policy import Policy
from collections import defaultdict, namedtuple

cache = SimpleCache()
#r_cache = RedisCache(key_prefix='dwr_cache')


def parse_links(links):
    pages = links.copy()
    for page, url in links.items():
        p = parse_link_url(url)
        pages[page] = p
    return pages


def parse_link_url(d):
    if d:
        s = d.get('url')
        if s:
            return s.split('=')[-1]
    return None


class NRClient:
    def __init__(self):
        self.links = None  # cache of the last request's "links" header, in case it's something likely to have links
        self.redis = redis.Redis()

    def _get(self, url, data=None, verbose=False):
        headers = {'X-Api-Key': app.config['NEW_RELIC_KEY']}
        if verbose:
            print 'data', data
        result = requests.get(url, headers=headers, data=data)
        if verbose:
            print result.headers.get('Link')
        self.links = parse_links(result.links)
        return result.json()

    def _simple_object(self, singular_name):
        if singular_name not in NR_OBJECTS:
            raise NotImplementedError('The NR object %s has not been implemented yet.' % singular_name)
        plural_name = singular_name + 's'  # may not always be true? good enough for "simple"...
        key_name = 'new_relic_' + plural_name
        klass = NR_OBJECTS[singular_name].klass
        url = NR_OBJECTS[singular_name].url
        j = cache.get(key_name)
        if j is None:
            j = self._get(url)
            cache.set(key_name, j)
        labels = [klass(x) for x in j.get(plural_name, j.get(singular_name)) if x is not None]
        return labels

    def get_apps(self, search_string=None, page=None):
        page_links = None
        data = {}
        if search_string is not None:
            data['filter[name]'] = search_string
        if page is not None and page > 1:
            data['page'] = page
        j = self._get(URL_APPS, data)
        apps = [App(x) for x in j.get('applications')]
        page_links = self.links
        # print '\n'.join(str(x) for x in apps)
        app_lookup = {x.id: x for x in apps}
        labels = self.get_labels()
        for label in labels:
            label_name = label.name
            for a in label.apps:
                if a in app_lookup:
                    app_lookup[a].labels.append(label_name)
        policies_to_apps = defaultdict(list)
        for app in apps:
            policies_to_apps[app.policy_id].append(app)
        r_channels = cache.get('new_relic_channels')
        if r_channels is None:
            r_channels = self._get(URL_CHANNEL)
            cache.set('new_relic_channels', r_channels)
        channels = [Channel(x) for x in r_channels.get('channels', [])]
        for c in channels:
            if c.type == 'pagerduty':
                for p in c.policies:
                    for app in policies_to_apps[p]:
                        app.channels.append(c.name)
        return apps, page_links

    def get_labels(self):
        return self._simple_object('label')

    def get_policies(self):
        j = self._get(URL_POLICY)
        policies = [Policy(x) for x in j.get('policies', [])]
        p_lookup = {x.id: x for x in policies}
        r_channels = self._get(URL_CHANNEL)
        channels = [Channel(x) for x in r_channels.get('channels', [])]
        for c in channels:
            if c.type == 'pagerduty':
                for p in c.policies:
                    p_lookup[p].channels.append(c.name)
        return policies

    def get_conditions_for_policy(self, policy_id):
        j = cache.get('conditions_for_policy_%s' % policy_id)
        if j is None:
            data = {'policy_id': policy_id}
            j = self._get(URL_CONDITION_APM, data=data)
            cache.set('conditions_for_policy_%s' % policy_id, j)
        c = j.get('conditions', [])
        conditions = [Condition(x) for x in c]
        return conditions

    def get_contacts(self):
        return self._simple_object('channel')

    def refresh_app_list(self, page):
        data = {'page':page}
        j = self._get(URL_APPS, data)
        apps = j.get('applications', j.get('application', []))
        app_id_names =[{'id':x['id'], 'name':x['name']} for x in apps]
        return app_id_names, self.links

    def set_app_list(self, apps):
        j = json.dumps(apps)
        return self.redis.set('dwr_newrelic_master_app_list', j)

    def get_app_list(self):
        as_string = self.redis.get('dwr_newrelic_master_app_list')
        j = json.loads(as_string)
        return j



class Condition:
    def __init__(self, j):
        if j:
            self.id = j.get('id')
            self.type = j.get('type')
            self.name = j.get('name')
            self.enabled = j.get('enabled', 'false') == 'true'
            self.entities = j.get('entities')
            self._metric = j.get('metric')
            self.terms = [Term(x) for x in j.get('terms')]
            self.user_defined = j.get('user_defined', {})
            if self._metric == 'user_defined' and 'metric' in self.user_defined.keys():
                self.metric = self.user_defined.get('metric')
            else:
                self.metric = self._metric

    def term_strings(self):
        if self.terms:
            sorted_terms = sorted(self.terms, cmp=lambda x, y: cmp(x.priority, y.priority), reverse=True)
            print sorted_terms
            return [str(x) for x in sorted_terms]
        return None




URL_LABELS = 'https://api.newrelic.com/v2/labels.json'
URL_CONDITION_APM = 'https://api.newrelic.com/v2/alerts_conditions.json'
URL_CONDITION_PLUGINS = 'https://api.newrelic.com/v2/alerts_plugins_conditions.json'
URL_CONDITION_EXTERNAL_SERVICES = 'https://api.newrelic.com/v2/alerts_external_service_conditions.json'

class NewRelicObject:
    def __init__(self, url, klass):
        self.url = url
        self.klass = klass

NR_OBJECTS = {
    'app': App,
    'label': Label,
    'channel': Channel,
}
