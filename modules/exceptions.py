class VersionError(Exception):
    """ Exception raised for various version errors. """
    def __init__(self, modulename: str, v_found: str, v_req: str):
        self.v_found = v_found
        self.v_req = v_req
        super().__init__(f'{modulename} version <{v_found}> initialized. Expected: <{v_req}>')


class LogicError(Exception):
    """ Exception raised for logical errors. """
    def __init__(self, msg: str):
        super().__init__(msg)
