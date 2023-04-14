

class LoopError(Exception):
    ''' Exception raised when a pseudorandom loop hits the defined attempt limit '''

    def __init__(self, msg: str | None, placed: int, target: int, loop_limit: int):
        self.msg = f'loop limit of {loop_limit} hit:\n'
        self.msg += f'  {placed} out of {target} objects placed/checked.\n'
        if msg:
            self.msg += f'  info: {msg}'
        super().__init__(f'\n< {self.msg} >')


class ConfigError(Exception):
    ''' Exception raised for config errors. pass the relevant config dict to print it. '''

    def __init__(self, msg: str, relevant_config: dict | None):
        self.relevant_config = relevant_config
        # create message, adding relevant config
        self.msg = msg
        if self.relevant_config:
            self.msg += f'\n[Relevant config dict: {self.relevant_config}]\n'
        super().__init__(f'< {self.msg} >')
