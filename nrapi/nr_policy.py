URL_POLICY = 'https://api.newrelic.com/v2/alerts_policies.json'

class Policy:
    def __init__(self, j):
        self.url = URL_POLICY
        if j:
            self.id = j.get('id')
            self.name = j.get('name')
            self.created = j.get('created')
            self.channels = []
