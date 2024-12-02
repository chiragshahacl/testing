from authentication.broker.publisher import PublisherBackend


class ConsolePublisher(PublisherBackend):
    def notify(
        self,
        entity_id: str,
        event_name: str,
        performed_by: str,
    ) -> None:
        schema = self.get_schema(entity_id, event_name, performed_by)
        message = str.encode(schema.model_dump_json())

        print("========= Publishing Notification =========")
        print(message)
        print("========= Notification Published  =========")
