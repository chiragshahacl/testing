export type SearchByNameParams = {
  firstName: string;
  lastName: string;
  dob?: string;
};

export type SearchByIdParams = {
  patientPrimaryIdentifier: string;
};

export type ServerSearchByNameParams = {
  givenName: string;
  familyName: string;
  birthDate?: string;
};

export type ServerSearchByIdParams = {
  patientIdentifier: string;
};
