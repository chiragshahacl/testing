/**
 * Here is the implementation of the butterworth filters used to smooth waveform data before
 * being shown in a graph
 */

export class SOBWHighPassFilter {
  private a: number[] = [0, 0, 0];
  private b: number[] = [0, 0, 0];
  private x: number[] = [0, 0, 0];
  private y: number[] = [0, 0, 0];

  constructor(samplingRate: number, halfPowerFrequency: number) {
    const alpha: number = Math.tan((Math.PI * halfPowerFrequency) / samplingRate);
    const alphaSq = alpha * alpha;
    const r: number = Math.sin(Math.PI / 4);
    const s = alphaSq + 2 * alpha * r + 1;
    const fa = 1 / s;
    const d1 = (2 * (1 - alphaSq)) / s;
    const d2 = -(alphaSq - 2 * alpha * r + 1) / s;
    this.b[0] = fa;
    this.b[1] = -2 * fa;
    this.a[1] = -d1;
    this.a[2] = -d2;
  }

  feedDatum(x0: number): number {
    this.x[2] = this.x[1];
    this.x[1] = this.x[0];
    this.x[0] = x0;
    this.y[2] = this.y[1];
    this.y[1] = this.y[0];
    this.y[0] =
      this.b[0] * (this.x[0] + this.x[2]) +
      this.b[1] * this.x[1] -
      this.a[1] * this.y[1] -
      this.a[2] * this.y[2];
    return this.y[0];
  }
}

export class SOBWLowPassFilter {
  private a: number[] = [0, 0, 0];
  private b: number[] = [0, 0, 0];
  private x: number[] = [0, 0, 0];
  private y: number[] = [0, 0, 0];

  constructor(samplingRate: number, halfPowerFrequency: number) {
    const alpha: number = Math.tan((Math.PI * halfPowerFrequency) / samplingRate);
    const alphaSq = alpha * alpha;
    const r: number = Math.sin(Math.PI / 4);
    const s = alphaSq + 2 * alpha * r + 1;
    const fa = alphaSq / s;
    const d1 = (2 * (1 - alphaSq)) / s;
    const d2 = -(alphaSq - 2 * alpha * r + 1) / s;
    this.b[0] = fa;
    this.b[1] = 2 * fa;
    this.a[1] = -d1;
    this.a[2] = -d2;
  }

  feedDatum(x0: number): number {
    this.x[2] = this.x[1];
    this.x[1] = this.x[0];
    this.x[0] = x0;
    this.y[2] = this.y[1];
    this.y[1] = this.y[0];
    this.y[0] =
      this.b[0] * (this.x[0] + this.x[2]) +
      this.b[1] * this.x[1] -
      this.a[1] * this.y[1] -
      this.a[2] * this.y[2];
    return this.y[0];
  }
}
