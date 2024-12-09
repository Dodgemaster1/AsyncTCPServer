class PortInUseError(OSError):
    def __init__(self, port):
        self.port = port
        self.message = f"Port is already in use: {port}"
        super().__init__(self.message)

class InitializeConnectionError(Exception):
    def __init__(self, e):
        super().__init__(e)

class ModemNotFound(InitializeConnectionError):
    def __init__(self, modem_number):
        message = f"Modem {modem_number} not found"
        super().__init__(message)


class ConnectionMessageError(InitializeConnectionError):
    def __init__(self, e):
        message = f'Connection message error: {e}'
        super().__init__(message)


class InvalidModemNumberError(InitializeConnectionError):
    def __init__(self, conn_message):
        message = f"Invalid modem number: {conn_message}"
        super().__init__(message)
