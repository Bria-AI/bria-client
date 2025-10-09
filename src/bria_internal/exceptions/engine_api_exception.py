class EngineAPIBaseException(Exception):
    def __init__(self, message: str, route: str, base_url: str, **kwargs):
        self.message = message
        self.route = route
        self.base_url = base_url
        self.kwargs = kwargs

        super().__init__(self.message)
