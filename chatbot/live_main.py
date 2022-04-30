"""
The interactive CIS main file.
Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from cis import CIS
from core import retriever
from core.input_handler.dialog_manager import DialogManager
from core.output_handler.simple_output_selection import SimpleOutputSelection
from util.logging import Logger


class ConvQA(CIS):
    def __init__(self, params):
        """
        The constructor for Conversational Question Answering. This is a Conversational application class and is
        inherited from the CIS class.
        Args:
            params(dict): A dict of parameters. These are mandatory parameters for this class: 'logger' which is an
            instance of the util.logging.Logger class. ConvQA requires both a retrieval and machine reading
            comprehension engines. Each of them requires some additional parameters. Refer to the corresponding class
            for more information on the required parameters.
        """
        super().__init__(params)
        self.logger = params['logger']
        self.logger.info('Conversational QA Model... starting up...')
        self.request_dispatcher = DialogManager(self.params)
        self.output_selection = SimpleOutputSelection(self.params)

    def request_handler_func(self, conv_list):
        """
        This function is called for each conversational interaction made by the user. In fact, this function calls the
        dispatcher to send the user request to the information seeking components.
        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
        Returns:
            output_msg(Message): Returns an output message that should be sent to the UI to be presented to the user.
        """
        self.logger.info(conv_list)
        dispatcher_output = self.request_dispatcher.dispatch(conv_list)
        output_msg = self.output_selection.get_output(conv_list, dispatcher_output)
        return output_msg

    def run(self):
        """
            This function is called to run the ConvQA system. In live mode, it never stops until the program is killed.
        """
        self.interface.run()


if __name__ == '__main__':
    basic_params = {'timeout': 15,  # timeout is in terms of second.
                    'mode': 'live',  # mode can be either live or exp.
                    'logger': Logger({})}  # for logging into file, pass the filepath to the Logger class.

    # These are required database parameters if the mode is 'live'. The host and port of the machine hosting the
    # database, as well as the database name.
    db_params = {'interaction_db_host': 'localhost',
                 'interaction_db_port': 27017,
                 'interaction_db_name': 'macaw_test'}

    # These are interface parameters. They are interface specific.
    interface_params = {'interface': 'stdio'}

    # These are parameters used by the retrieval model.
    retrieval_params = {'conf dataset': 'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\conference_data.json',
                        'index path': 'D:/ERSP/chatbot/input_handler',
                        'arxiv path': 'C:\\Users\\snipe\\Documents\\GitHub\\ERSP\\arxiv_parsed.json',
                        'DA list': []}

    params = {**basic_params, **db_params, **interface_params, **retrieval_params}
    basic_params['logger'].info(params)
    ConvQA(params).run()