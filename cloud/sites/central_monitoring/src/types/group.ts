import { BedType, ServerBed } from './bed';

export interface GroupType {
  id: string;
  name: string;
  description?: string;
  beds: BedType[];
}

export interface NewGroupType {
  id: string | undefined;
  name: string;
  description?: string;
  beds: BedType[];
}

export interface ServerGroup {
  id: string;
  name: string;
  description?: string;
  beds: ServerBed[];
}

export interface CreateUpdateBedGroupData {
  id?: string;
  name: string;
}

export interface AssignBedGroupData {
  group_id: string;
  bed_ids: string[];
}
