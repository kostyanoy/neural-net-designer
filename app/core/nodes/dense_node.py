from NodeGraphQt import BaseNode


class DenseNode(BaseNode):
    __identifier__ = 'neural_net'
    NODE_NAME = 'Dense'

    def __init__(self):
        super(DenseNode, self).__init__()
        self.add_input('input')
        self.add_output('output')
        self.add_text_input("units", "Units:", text="64", tab="properties")
        self.add_text_input("activation", "Activation:", text="relu", tab="properties")