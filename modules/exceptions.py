from constants.config import CONFIG as CF


class VersionError(Exception):
    ''' Exception raised for various version errors.\n
        Will abort the program if config version_error_fatal is set, otherwise just print '''

    def __init__(self, modulename: str, v_found: str, v_req: str):
        self.msg = f'{modulename} version <{v_found}> initialized. Expected: <{v_req}>'

        if CF['exceptions']['version_error_fatal']:
            self.msg = f'[FATAL]: {self.msg}'
            super().__init__(self.msg)
        else:
            self.msg = f'[VersionError]: {self.msg}'
            print(self.msg)


class LogicError(Exception):
    ''' Exception raised for logical errors.\n
        Will abort the program if config version_error_fatal is set, otherwise just print '''

    def __init__(self, msg: str):
        self.msg = msg

        if CF['exceptions']['version_error_fatal']:
            self.msg = f'[FATAL]: {self.msg}'
            super().__init__(self.msg)
        else:
            self.msg = f'[LogicError]: {self.msg}'
            print(self.msg)
