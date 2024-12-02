import { NextApiResponse } from 'next';

// eslint-disable-next-line no-empty-pattern
const handler = ({} = {}, res: NextApiResponse) => {
  res.json({
    APP_URL: process.env.APP_URL,
    WSS_URL: process.env.WSS_URL,
    EMULATOR_URL: process.env.EMULATOR_URL,
    HOSPITAL_TITLE: process.env.HOSPITAL_TITLE,
    HOSPITAL_TZ: process.env.HOSPITAL_TZ,
    MAX_NUMBER_BEDS: process.env.MAX_NUMBER_BEDS,
    HEALTHCHECK_INTERVAL: process.env.HEALTHCHECK_INTERVAL,
    IGNORE_BUTTERWORTH_FILTERS: process.env.IGNORE_BUTTERWORTH_FILTERS,
    SIBEL_VERSION: process.env.SIBEL_VERSION,
  });
  res.status(200);
};
export default handler;
