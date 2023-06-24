from multiprocessing import Process


class processing_multi(Process):

    def __init__(self, obj):
        super(processing_multi, self).__init__()
        self.obj = obj
        # self.hedge = hedge

    def run(self):
        [x.start() for x in self.obj]
        # self.hedge.hedge()