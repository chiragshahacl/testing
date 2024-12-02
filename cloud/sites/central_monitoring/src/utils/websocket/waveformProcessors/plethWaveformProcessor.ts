import { WaveformProcessor } from './WaveformProcessor';
import { SOBWHighPassFilter, SOBWLowPassFilter } from './butterWorthFilters';

export class PlethWaveformProcessor extends WaveformProcessor {
  hpf: SOBWHighPassFilter;
  lpf: SOBWLowPassFilter;
  constructor() {
    super();
    this.hpf = new SOBWHighPassFilter(64, 0.5);
    this.lpf = new SOBWLowPassFilter(64, 6.0);
  }

  override feedDatum(x: number): number | null {
    if (isNaN(x)) return null;
    return this.lpf.feedDatum(this.hpf.feedDatum(x)) * -1;
  }
}
