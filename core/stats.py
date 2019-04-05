class Counter:
    def __init__(self):
        self.counter = {}

    def inc(self, field, value=1):
        if field in self.counter:
            self.counter[field] += value
        else:
            self.counter[field] = 1

    def get_counter(self):
        return self.counter