URL_CHANNEL = 'https://api.newrelic.com/v2/alerts_channels.json'

class Channel:
    def __init__(self, j):
        self.url = URL_CHANNEL
        if j:
            self.id = j.get('id')
            self.name = j.get('name')
            self.type = j.get('type')
            self.policies = j.get('links', {}).get('policy_ids', [])

