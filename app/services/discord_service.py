class DiscordService:


    def receive_response(self, response):
        self.dispatch_messages(response)

    def dispatch_messages(self, response):
        for message in response.messages:
            destination = message["to"]
            body = message["body"]

            if message["type"] == "text":
                self.send_message(body, destination)

    def send_message(self, message, destination):
        print(f"\nTO: {destination}\n{message}")