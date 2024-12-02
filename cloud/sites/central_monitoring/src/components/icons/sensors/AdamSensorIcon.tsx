import { SENSOR_TYPES } from '@/types/sensor';
import { getAlertColor } from '@/utils/alertUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';

type Props = {
  alertPriority?: ALERT_PRIORITY;
};

const AdamSensorIcon = ({ alertPriority }: Props) => {
  const color = alertPriority ? getAlertColor(alertPriority) : 'white';

  return (
    <svg
      data-testid={`${SENSOR_TYPES.ADAM}-sensor-icon`}
      width='40'
      height='40'
      viewBox='0 0 40 40'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
    >
      <g clipPath='url(#clip0_1252_28354)'>
        <path
          fillRule='evenodd'
          clipRule='evenodd'
          d='M19.2174 4.1665C14.5863 4.1665 10.832 7.92075 10.832 12.5518V30.7866C10.832 32.5509 12.2622 33.981 14.0264 33.981H22.7415C23.5067 34.8002 24.5965 35.3123 25.806 35.3123C28.1216 35.3123 29.9987 33.4352 29.9987 31.1196C29.9987 29.447 29.0193 28.0032 27.6027 27.3303V12.5518C27.6027 7.92075 23.8485 4.1665 19.2174 4.1665ZM17.3008 18.5415C15.713 18.5415 14.4258 19.8287 14.4258 21.4165V26.4478C14.4258 28.0356 15.713 29.3228 17.3008 29.3228H21.1341C22.7219 29.3228 24.0091 28.0356 24.0091 26.4478V21.4165C24.0091 19.8287 22.7219 18.5415 21.1341 18.5415H17.3008ZM16.8216 11.354C16.8216 10.0308 17.8943 8.95817 19.2174 8.95817C20.5406 8.95817 21.6133 10.0308 21.6133 11.354V16.1457H16.8216V11.354Z'
          fill={color}
        />
      </g>
      <defs>
        <clipPath id='clip0_1252_28354'>
          <rect width='40' height='40' fill={color} />
        </clipPath>
      </defs>
    </svg>
  );
};

export default AdamSensorIcon;
