# -*- coding:Utf-8 -*-

import pyglet
from Classes.my_queue import DequeQueue as Queue


class BaseViewer(pyglet.window.Window):

    def __init__(self, fps, logger, *args, **kwargs):
        super(BaseViewer, self).__init__(*args, **kwargs)

        self.logger = logger
        self.fps = fps
        self.dt = 1. / fps

        self.virtual_events_queue = Queue()
        self.virtual_events_bindings = dict()

        pyglet.clock.schedule_interval(self.update, self.dt)

    def bind(self, event_manager):
        if not hasattr(event_manager, 'get_handlers'):
            raise AttributeError('event_manager must have a "get_handlers" method.')
        for name, func in event_manager.get_handlers().items():
            self.set_handler(name, func)
        if hasattr(event_manager, 'get_virtual_handlers'):
            for event_id, func in event_manager.get_virtual_handlers().items():
                self._bind_virtual_event(event_id, func)

    def unbind(self, event_manager):
        if not hasattr(event_manager, 'get_handlers'):
            raise AttributeError('event_manager must have a "get_handlers" method.')
        for name, func in event_manager.get_handlers().items():
            self.remove_handler(name, func)
        if hasattr(event_manager, 'get_virtual_handlers'):
            for event_id in event_manager.get_virtual_handlers():
                self._unbind_virtual_event(event_id)

    def _bind_virtual_event(self, event_id, callback):
        self.virtual_events_bindings[event_id] = callback

    def _unbind_virtual_event(self, event_id):
        del self.virtual_events_bindings[event_id]

    def post(self, event_id):
        self.virtual_events_queue.put(event_id)

    def update(self, *args, **kwargs):
        for event in self.virtual_events_queue.elements():
            try:
                self.virtual_events_bindings[event]()
            except KeyError:
                pass


class BaseViewer0:

    def __init__(self, framerate, logger):
        self.logger = logger
        self.logger.debug('initialize BaseViewer')
        self.stop_mainloop = False
        self.events = dict()
        self.actions = set()
        self.FRAMERATE = framerate
        self.clock = pygame.time.Clock()

        self.window = None

    def wdisplay(self, window_size, flags=tuple()):
        self.window = pygame.display.set_mode(window_size, *flags)

    def stop_loop(self):
        self.logger.info('Stopping loop...')
        self.stop_mainloop = True

    def loop(self):
        while not self.stop_mainloop:
            self.clock.tick(self.FRAMERATE)
            for event in pygame.event.get():

                if event.type in self.events.keys():
                    self.events[event.type](event)

                elif event.type == QUIT:
                    self.logger.warning('The game has been force-quited.')
                    return -1

                elif event.type == MOUSEBUTTONDOWN:
                    self.logger.debug(str(self.clock.get_fps()))
            pygame.event.pump()

            for action in self.actions:
                action()

            self.main()

            pygame.display.flip()

        self.logger.info('Done.')
        return 0

    def main(self):
        raise NotImplementedError('Implement this method in subclasses of this class.')
