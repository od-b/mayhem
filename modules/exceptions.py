class VersionError(Exception):
    ''' Exception raised for various version errors. '''

    def __init__(self, modulename: str, v_found: str, v_req: str):
        self.msg = f'\n< {modulename} version "{v_found}" initialized. Expected: "{v_req}" >'
        super().__init__(self.msg)


class LogicError(Exception):
    ''' Exception raised for logical errors.'''

    def __init__(self, msg: str):
        self.msg = f'\n< {msg} >'
        super().__init__(self.msg)


class ConfigError(Exception):
    ''' Exception raised for config errors. pass the relevant config dict to print it. '''

    def __init__(self, msg: str, relevant_config: dict | None):
        self.relevant_config = relevant_config
        # create message, adding relevant config
        self.msg = f'\n< {msg} '
        if self.relevant_config:
            self.msg += f'\n[Relevant config dict: {self.relevant_config}]\n'
        super().__init__(self.msg+'>')
