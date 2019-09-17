class DefaultContext:
    def __init__(self, label):
        self.label = label

    def __getitem__(self, item):
        return self.label


class EcflowContext:
    def __init__(self, label):
        self.label = label
        self._context = self._parse(label)

    def _parse(self, filename):
        pass

    def __getitem__(self, item):
        return self._context[item]