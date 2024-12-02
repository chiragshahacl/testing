import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { translationFile } from '@/utils/translation';

void i18n.use(initReactI18next).init({
  resources: translationFile,
  lng: 'en',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
