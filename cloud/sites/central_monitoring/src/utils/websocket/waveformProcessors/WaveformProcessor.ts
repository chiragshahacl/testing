import { SOBWHighPassFilter, SOBWLowPassFilter } from './butterWorthFilters';

export abstract class WaveformProcessor {
  abstract hpf: SOBWHighPassFilter;
  abstract lpf: SOBWLowPassFilter;

  feedDatum(x: number): number | null {
    if (isNaN(x)) {
      return null;
    }
    return this.lpf?.feedDatum(this.hpf?.feedDatum(x));
  }
}
