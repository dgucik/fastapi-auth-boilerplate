from dataclasses import dataclass


@dataclass(frozen=True)
class ExceptionMetadata:
    status_code: int
    error_code: str


class ExceptionRegistry:
    def __init__(
        self,
        mappings_list: list[dict[type[Exception], ExceptionMetadata]] | None = None,
    ) -> None:
        self._mappings: dict[type[Exception], ExceptionMetadata] = {}
        if mappings_list:
            for mapping in mappings_list:
                self._mappings.update(mapping)

    def get_metadata(self, exc: Exception) -> ExceptionMetadata | None:
        for cls in type(exc).mro():
            if cls in self._mappings:
                return self._mappings[cls]
        return None
