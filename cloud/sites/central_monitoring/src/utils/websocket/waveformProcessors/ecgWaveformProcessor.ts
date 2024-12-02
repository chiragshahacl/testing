import { WaveformProcessor } from './WaveformProcessor';
import { SOBWHighPassFilter, SOBWLowPassFilter } from './butterWorthFilters';

export class EcgWaveformProcessor extends WaveformProcessor {
  hpf: SOBWHighPassFilter;
  lpf: SOBWLowPassFilter;
  constructor(sampleRate: number) {
    super();
    this.hpf = new SOBWHighPassFilter(sampleRate, 0.5);
    this.lpf = new SOBWLowPassFilter(sampleRate, 20.0);
  }
}
