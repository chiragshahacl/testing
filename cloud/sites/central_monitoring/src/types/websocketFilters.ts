export interface WebsocketFiltersMessage {
  patientIdentifiers: string[];
  filters: {
    codes?: string[];
    patientFilters?: {
      identifier: string;
      codes: string[];
    };
  };
  sendCache?: boolean;
}
