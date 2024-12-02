import { openSansFont } from '@/utils/fonts';

const typography = {
  allVariants: {
    fontFamily: openSansFont.style.fontFamily,
    letterSpacing: 0,
  },
  h1: {
    fontSize: '40px',
    fontWeight: '700',
    lineHeight: '48px',
  },
  h2: {
    fontSize: '24px',
    fontWeight: '700',
    lineHeight: '28px',
  },
  h3: {
    fontFamily: openSansFont.style.fontFamily,
    fontSize: '14px',
    fontWeight: '700',
    lineHeight: '19.07px',
    color: '#979797',
  },
  h4: {
    fontSize: '17px',
    fontWeight: '400',
    lineHeight: '19.53px',
  },
  h5: {
    fontSize: '18px',
    fontWeight: '700',
    lineHeight: '26px',
  },
  h6: {
    fontSize: '16px',
    fontWeight: '700',
    lineHeight: '21.79px',
  },
  button: {
    fontSize: '24px',
    fontWeight: '700',
    lineHeight: '26px',
    textTransform: 'none' as const,
  },
  subtitle1: {
    fontSize: '21px',
    fontWeight: '400',
    lineHeight: '150%',
  },
  subtitle2: {
    fontSize: '14px',
    fontWeight: '400',
    lineHeight: '19px',
  },
  body1: {
    fontSize: '18px',
    fontWeight: '400',
    lineHeight: '25px',
  },
  body2: {
    fontSize: '16px',
    fontWeight: '600',
    lineHeight: '24px',
  },
  body3: {
    fontSize: '20px',
    fontWeight: '700',
    lineHeight: '23px',
  },
  bodySmall: {
    fontSize: '13px',
    fontWeight: '400',
    lineHeight: '17.7px',
  },
  metricNumberStyles: {
    fontSize: '34px',
    lineHeight: '46px',
    fontWeight: 600,
    fontFamily: openSansFont.style.fontFamily,
  },
  caption: {
    fontSize: '16px',
    fontWeight: '400',
    lineHeight: '24px',
  },
  error: {
    fontSize: '18px',
    fontWeight: '600',
    lineHeight: '27px',
    color: '#E95454',
  },
  overline: {
    fontFamily: openSansFont.style.fontFamily,
    fontSize: '17px',
    fontWeight: '600',
    lineHeight: '24px',
    color: '#C4C4C4',
  },
};

export default typography;
