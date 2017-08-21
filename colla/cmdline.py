def _iter_command_classes(module_name):
    # TODO: add `name` attribute to commands and and merge this function with
    # scrapy.utils.spider.iter_spider_classes
    for module in walk_modules(module_name):
        for obj in vars(module).itervalues():
            if inspect.isclass(obj) and \
               issubclass(obj, ScrapyCommand) and \
               obj.__module__ == module.__name__:
                yield obj


class BaseCommand(object):

    name = 'base'

    def run(self, *args, **kwargs):

        raise NotImplementedError('BaseCommand subclass must implement run method')


class WorkerCommand(BaseCommand):

    name = 'work'

    def run(self, *args, **kwargs):
        worker_name = ''

        engine = Engine.from_settings(settings)
        engine.create_worker(worker_name)
        engine.run()



# 
# def execute():
#     import os
#     import django
#     os.environ['DJANGO_SETTINGS_MODULE'] = 'orm.settings'
#     django.setup()
#
#
#     engine.create_worker('new_beijing_web')
#     engine.run()
