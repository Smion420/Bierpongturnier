class Ok:
    def __init__(self, message: str = "OK", data: any = None):
        self.message = message
        self.data = data
    
class Error:
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message