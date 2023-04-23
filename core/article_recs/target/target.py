class Target:

    def send(self, content_id: str, image_url: str, text: str):
        pass

class Handler:
    def handle(self, contnent_id: str, data: dict) -> None:
        pass
