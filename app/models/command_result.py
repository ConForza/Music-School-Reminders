class CommandResult:

    def __init__(self, type_, content=None, errors=None, routing=None, source=None):
        self.type_ = type_
        self.content = content or {}
        self.errors = errors or []
        self.routing = routing
        self.source = source
