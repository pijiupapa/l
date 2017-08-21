from colla.utils import get_class_from_module_path
from colla.pipeline import Pipeline, DummyPipeline

class Worker(object):

    pipe_name = ""
    def __init__(self, engine):
        self.engine = engine
        self.pipeline = self.get_pipeline()

    def get_pipeline(self):
        pipeline_cls = DummyPipeline
        if self.pipe_name:
            module_path = 'pipelines.' + self.pipe_name
            pipeline_cls = get_class_from_module_path(module_path, Pipeline)
        return pipeline_cls(self.engine)

    @property
    def scheduler(self):
        return self.engine.scheduler


    def execute_before(self, task):
        pass

    def execute(self, task):
        raise NotImplementedError('Worker class must implement execute')

    def execute_after(self, task):
        pass

    def handle_exception(self, error):
        return False


    def close(self):
        pass

    def adsl(self):
        from adsl.ppoe.client import ppoe_client
        self.before_adsl()
        ppoe_client.reconnect()
        self.after_adsl()

    def before_adsl(self):
        pass

    def after_adsl(self):
        pass
