from pydantic import Field

from src.common.schemas_base import BaseSchema
from src.realtime.subscriber import (
    MetricCodeFilter,
    PatientFilter,
    SubscriptionFilter,
)


class PatientFilters(BaseSchema):
    identifier: str
    codes: list[str]


class VitalsFiltersSchema(BaseSchema):
    codes: list[str]
    patient_filters: PatientFilters | None = Field(default=None, alias="patientFilters")
    filter_backfill: bool = Field(default=True, alias="filterBackfill")

    def to_filters(self) -> list[SubscriptionFilter]:
        filters = []
        if self.codes:
            filters.append(MetricCodeFilter(codes=self.codes))
        if self.patient_filters:
            filters.append(
                PatientFilter(self.patient_filters.identifier, self.patient_filters.codes)
            )
        return filters


class WSSubscription(BaseSchema):
    filters: VitalsFiltersSchema
    patient_identifiers: list[str] = Field(default=[], alias="patientIdentifiers")
    send_cache: bool = Field(default=False, alias="sendCache")
