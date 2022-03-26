class debugger:
    
    #TODO Support UART output possibly in signalk format

    def __init__(self, enable: bool = False) -> None:
        self.enable = enable

    def print(self, message: str):
        
        if self.enable:
            print(message)