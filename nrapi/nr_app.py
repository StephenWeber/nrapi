HEALTH_STATES = []


class App:
    def __init__(self, j):
        self.url = 'https://api.newrelic.com/v2/applications.json'
        if j:
            self.id = j.get('id')
            self.name = j.get('name')
            self.health_status = j.get('health_status')
            links = j.get('links')
            self.policy_id = links.get('alert_policy')
            self.hosts = links.get('application_hosts', [])
            self.instances = links.get('application_instances', [])
            self.servers = links.get('servers', [])
            self.channels = []
            self.application_summary = j.get('application_summary', {})
            self.end_user_summary = j.get('end_user_summary', {})
            self.labels = []

    def __str__(self):
        return ', '.join(['"%s":"%s"' % x for x in self.__dict__.items()])


"""{
    "id": "integer",
    "name": "string",
    "language": "string",
    "health_status": "string",
    "reporting": "boolean",
    "last_reported_at": "time",
    "application_summary": {
      "response_time": "float",
      "throughput": "float",
      "error_rate": "float",
      "apdex_target": "float",
      "apdex_score": "float",
      "host_count": "integer",
      "instance_count": "integer",
      "concurrent_instance_count": "integer"
    },
    "end_user_summary": {
      "response_time": "float",
      "throughput": "float",
      "apdex_target": "float",
      "apdex_score": "float"
    },
    "settings": {
      "app_apdex_threshold": "float",
      "end_user_apdex_threshold": "float",
      "enable_real_user_monitoring": "boolean",
      "use_server_side_config": "boolean"
    },
    "links": {
      "servers": [
        "integer"
      ],
      "application_hosts": [
        "integer"
      ],
      "application_instances": [
        "integer"
      ],
      "alert_policy": "integer"
    }
  }"""
