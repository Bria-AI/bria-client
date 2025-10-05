class ContentModerationError(Exception):
    def __init__(self, message: str, route: str, **kwargs):
        self.message = message
        self.route = route
        self.kwargs = kwargs
        super().__init__(self.message)
