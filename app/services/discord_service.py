class DiscordService:


    def receive_response(self, response):
        self.dispatch_messages(response)
        if len(response.errors) > 0:
            self.display_errors(response.errors)

    def dispatch_messages(self, response):
        for message in response.messages:
            destination = message["to"]
            body = message["body"]

            if message["type"] == "text":
                self.send_message(body, destination)

    def send_message(self, message, destination):
        print(message)

    def display_errors(self, errors):
        for error in errors:
            print(error)