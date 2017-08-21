# -*- coding=utf-8 -*-
import os
import socket
import logging
from colla.scheduler import Scheduler
from colla.task import Task
from colla.item import Item
from colla.worker import Worker
from colla.logger import LOGGING, logger
from colla.utils import get_class_from_module, import_module_object, reconnect_database
from colla.exceptions import ExitWithDone, ExitWithoutDone, ExitWithDoneNoAck
from colla.signals import engine_setup, engine_stop
from colla.raven_client import client



class Engine(object):


    def start(self, settings):
        self.settings = settings
        self.scheduler = Scheduler.from_settings(settings)
        self.workers_cls = self.load_all_wokers()
        self.current_task = None
        # self.setup_log()
        engine_setup.send(self)

    def setup_log(self):
        LOGGING['handlers']['info_file']['filename'] = "log/%s.log" % self.worker_cls.name
        logging.config.dictConfig(LOGGING)


    def load_all_wokers(self):
        return get_class_from_module(self.settings.workers_dir, Worker)


    def create_worker(self, name):
        if name not in self.workers_cls:
            raise Exception(u"no worker with name: %s" % name)
        worker_cls = self.workers_cls[name]
        self.worker = worker_cls(self)


    def run(self):
        logger.info("engine start running")
        self.scheduler.queue_declare(self.worker.queue)
        while True:
            try:
                task = self.scheduler.next_task(self.worker.queue)
                self.current_task = task
                self.worker.execute_before(task)
                response_yield = self.worker.execute(task)
                for response in response_yield:
                    assert isinstance(response, Item) or response is None

                    if isinstance(response, Item):
                        ret = self.worker.pipeline.process_item(response)
                        if ret is not None:
                            task.meta.update(ret)
                    else:
                        task.ack()
                        break

                self.worker.execute_after(task)

            except ExitWithoutDone:
                logger.info("exit without done")
                task.in_queue()
                task.ack()
                self.worker.execute_after(task)

            except ExitWithDone:
                logger.info("task finished")
                task.ack()
                self.worker.execute_after(task)

            except ExitWithDoneNoAck:
                logger.info("exit without done, no ack")
                self.worker.execute_after(task)

            except KeyboardInterrupt, error:
                self.worker.handle_exception(error)
                self.stop()
                return

            except socket.timeout, error:
                self.worker.handle_exception(error)
                logger.exception("socket timeout")
                logger.info("try to reconnect database and rabbitmq")
                reconnect_database()
                engine.scheduler.reconnect()


            except Exception, error:
                ret = self.worker.handle_exception(error)
                if not ret:
                    client.captureException()
                    logger.info("worker not handler")
                    logger.exception("uncaught exception")
                    self.stop()
                    raise
                    return


    def stop(self):
        logger.info("engine is stopping")
        engine_stop.send(self)


engine = Engine()
