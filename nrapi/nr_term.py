
class Term:
    def __init__(self, j):
        if j:
            self.duration = j.get('duration')
            self.operator = j.get('operator')
            self.priority = j.get('priority')
            self.threshold = j.get('threshold')
            self.time_function = j.get('time_function')

    def __str__(self):
        return '%(time_function)s %(operator)s %(threshold)s over %(duration)sm - %(priority)s' % self.__dict__

