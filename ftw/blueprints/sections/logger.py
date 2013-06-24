from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.utils import Expression
from zope.interface import classProvides, implements
import logging


class Logger(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.print_out = Expression(
            options.get('print_out'), transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:
            self.logger.info(str(self.print_out(item)))
            yield item
            continue
