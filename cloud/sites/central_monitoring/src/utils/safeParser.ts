import { toNumber } from 'lodash';

export class SafeParser {
  static toFixed = (value: unknown, fractionDigits?: number): string => {
    const numberValue = toNumber(value);
    return !isNaN(numberValue) ? numberValue.toFixed(fractionDigits) : '';
  };
}
