
class Pipeline(object):

    def __init__(self, engine):
        self.engine = engine

    def process_item(self, item):
        raise NotImplementedError('Pipeline class must implement process_item')

class DummyPipeline(Pipeline):

    def process_item(self, item):
        pass
