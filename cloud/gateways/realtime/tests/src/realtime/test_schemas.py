from src.realtime.schemas import PatientFilters, VitalsFiltersSchema
from src.realtime.subscriber import BackfillFilter, MetricCodeFilter, PatientFilter


class TestVitalsFiltersSchema:
    def test_to_filters_only_codes(self):
        codes = ["1234", "4321"]
        payload = VitalsFiltersSchema.model_construct(codes=codes, filter_backfill=False)
        expected_filter = MetricCodeFilter(codes=codes)

        result = payload.to_filters()

        assert len(result) == 1

        found_filter = result[0]
        assert isinstance(found_filter, MetricCodeFilter)
        assert found_filter.codes == expected_filter.codes

    def test_to_filters_with_patient_override(self):
        codes = ["1", "2"]
        payload = VitalsFiltersSchema.model_construct(
            codes=codes,
            patient_filters=PatientFilters.model_construct(identifier="patient", codes=["3", "4"]),
            filter_backfill=False,
        )
        expected_metric_filter = MetricCodeFilter(codes=codes)
        expected_patient_filter = PatientFilter(identifier="patient", codes=["3", "4"])

        result = payload.to_filters()

        assert len(result) == 2

        metric_filter, patient_filter = result
        assert isinstance(metric_filter, MetricCodeFilter)
        assert isinstance(patient_filter, PatientFilter)

        assert metric_filter.codes == expected_metric_filter.codes
        assert patient_filter.codes == expected_patient_filter.codes
        assert patient_filter.identifier == expected_patient_filter.identifier
