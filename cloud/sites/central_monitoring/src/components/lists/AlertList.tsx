import { AlertPriorityIndicator } from '@/styles/StyledComponents';
import { Alert, DeviceAlert, VitalsAlert } from '@/types/alerts';
import { SENSOR_TYPES } from '@/types/sensor';
import {
  ALERT_TEXT_COLOR,
  getAlertColor,
  getAlertPriorityValue,
  getDeviceAlert,
  getHighestPriorityAlertColor,
  getHighestPriorityAlertTitle,
  getVitalAlert,
  isMonitorNotAvailableAlertPresent,
} from '@/utils/alertUtils';
import { openSansFont } from '@/utils/fonts';
import { ALERT_TYPES, DEVICE_ALERT_CODES, DEVICE_CODES } from '@/utils/metricCodes';
import { parseMoment } from '@/utils/moment';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import { Theme, styled, useTheme } from '@mui/material/styles';
import React, { ReactNode, useEffect, useRef, useState } from 'react';
import NumberBadge from '../NumberBadge';
import { DownFullArrowIcon } from '../icons/FullArrowIcon';

interface StyledMenuProps {
  width: string;
  bordercolor: string;
  backgroundcolor: string;
  theme: Theme;
}

const StyledAlertsMenu = styled(Menu)((props: StyledMenuProps) => ({
  ul: {
    backgroundColor: props.backgroundcolor,
  },
  li: {
    backgroundColor: props.backgroundcolor,
    borderRadius: 16,
  },
  '.MuiMenu-paper': {
    border: `2px solid ${props.bordercolor}`,
    borderRadius: props.theme.spacing(0, 0, 16, 16),
    width: props.width,
    maxHeight: 346,
    padding: 5,
  },
}));

const buttonStyles = {
  display: 'flex',
  flex: 1,
  flexDirection: 'row',
  justifyContent: 'space-between',
  fontStyle: 'normal',
  fontWeight: 500,
  fontSize: 16,
  lineHeight: 28,
  marginLeft: 8,
  color: ALERT_TEXT_COLOR,
};

interface AlertListProps {
  deviceAlerts: DeviceAlert[];
  vitalsAlerts: VitalsAlert[];
  containerStyles?: React.CSSProperties;
}

const AlertList = ({ deviceAlerts, vitalsAlerts, containerStyles = {} }: AlertListProps) => {
  const theme = useTheme();
  const targetRefDevice = useRef<HTMLButtonElement>(null);
  const targetRefVitals = useRef<HTMLButtonElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0 });
  const [anchorElDevice, setAnchorElDevice] = useState<null | HTMLElement>(null);
  const [anchorElVitals, setAnchorElVitals] = useState<null | HTMLElement>(null);

  const openDevice = Boolean(anchorElDevice && deviceAlerts?.length > 0);
  const handleClickDevice = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setAnchorElDevice(event.currentTarget);
  };
  const handleCloseDevice = () => {
    setAnchorElDevice(null);
  };

  const openVitals = Boolean(anchorElVitals && vitalsAlerts.length > 0);
  const handleClickVitals = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setAnchorElVitals(event.currentTarget);
  };
  const handleCloseVitals = () => {
    setAnchorElVitals(null);
  };

  const handleResize = () => {
    if (targetRefDevice.current) {
      setDimensions({
        width: targetRefDevice.current.offsetWidth,
      });
    } else if (targetRefVitals.current) {
      setDimensions({
        width: targetRefVitals.current.offsetWidth,
      });
    }
  };

  const getElementWidth = () => {
    if (
      vitalsAlerts?.length > 0 &&
      deviceAlerts?.length > 0 &&
      !isMonitorNotAvailableAlertPresent(deviceAlerts)
    )
      return '50%';
    if (vitalsAlerts?.length > 0 || deviceAlerts?.length > 0) return '25%';
    return '0';
  };

  const renderAlerts = (type: ALERT_TYPES, alerts: DeviceAlert[] | VitalsAlert[]) => {
    const res: ReactNode[] = [];
    alerts
      .sort((a: Alert, b: Alert) =>
        a.priority === b.priority
          ? parseMoment(b.timestamp).diff(parseMoment(a.timestamp))
          : getAlertPriorityValue(b.priority) - getAlertPriorityValue(a.priority)
      )
      .forEach((alert: Alert) => {
        res.push(
          <MenuItem
            key={`alert_${alert.code}_${alert.deviceCode}`}
            disabled
            sx={{
              display: 'flex',
              flexDirection: 'row',
              justifyContent: 'space-between',
              width: '100%',
              padding: (theme) => theme.spacing(12, 8),
            }}
          >
            <AlertPriorityIndicator
              sx={{
                backgroundColor: getAlertColor(alert.priority),
              }}
            />
            <Grid display='flex' flexDirection='column' flex={1}>
              {type === ALERT_TYPES.DEVICE && (
                <Typography
                  color='common.white'
                  variant='bodySmall'
                  sx={{
                    fontFamily: openSansFont.style.fontFamily,
                    fontWeight: 700,
                  }}
                >
                  {Object.values(DEVICE_CODES).find((d) => d.type === alert.deviceCode)?.name}
                </Typography>
              )}
              <Typography variant='caption' color='common.white'>
                {type === ALERT_TYPES.VITALS
                  ? getVitalAlert(alert.code, alert.deviceCode as SENSOR_TYPES)?.message
                  : getDeviceAlert(alert.code, alert.deviceCode as SENSOR_TYPES)?.message}
              </Typography>
            </Grid>
          </MenuItem>
        );
      });
    return res;
  };

  const renderDeviceAlerts = () => {
    if (isMonitorNotAvailableAlertPresent(deviceAlerts)) {
      return renderAlerts(ALERT_TYPES.DEVICE, [
        deviceAlerts.find(
          (alert) => alert.code === DEVICE_ALERT_CODES.MONITOR_NOT_AVAILABLE_ALERT.code
        ) as DeviceAlert,
      ]);
    } else return renderAlerts(ALERT_TYPES.DEVICE, deviceAlerts);
  };

  const renderVitalsAlerts = () => {
    return renderAlerts(ALERT_TYPES.VITALS, vitalsAlerts);
  };

  useEffect(() => {
    // Resizes alert list when mounted and adds listener for resize event
    window.addEventListener('resize', handleResize);
    handleResize();
  }, []);

  useEffect(() => {
    // Resizes alert list when new alerts are received
    handleResize();
  }, [deviceAlerts, vitalsAlerts]);

  return (
    <Grid
      display='flex'
      flexDirection='row'
      width={getElementWidth()}
      onClick={(event) => {
        event.stopPropagation();
      }}
      sx={{
        overflow: 'hidden',
        ...containerStyles,
      }}
      position='relative'
    >
      {deviceAlerts?.length > 0 && (
        <>
          <Button
            data-testid='device-alerts-list'
            ref={targetRefDevice}
            onClick={handleClickDevice}
            sx={{
              ...buttonStyles,
              backgroundColor: getHighestPriorityAlertColor(deviceAlerts),
              '&:hover': {
                backgroundColor: getHighestPriorityAlertColor(deviceAlerts),
              },
            }}
          >
            <Typography variant='caption'>
              {getHighestPriorityAlertTitle(deviceAlerts, ALERT_TYPES.DEVICE)}
            </Typography>
            <Grid display='flex' flexDirection='row'>
              <NumberBadge
                number={isMonitorNotAvailableAlertPresent(deviceAlerts) ? 1 : deviceAlerts?.length}
                color={getHighestPriorityAlertColor(deviceAlerts)}
              />
              <DownFullArrowIcon color={ALERT_TEXT_COLOR} />
            </Grid>
          </Button>
          <StyledAlertsMenu
            theme={theme}
            anchorEl={anchorElDevice}
            open={openDevice}
            onClose={handleCloseDevice}
            onClick={(event) => {
              event.stopPropagation();
            }}
            width={dimensions.width.toString() + 'px'}
            backgroundcolor='disabled'
            bordercolor={getHighestPriorityAlertColor(deviceAlerts)}
          >
            {renderDeviceAlerts()}
          </StyledAlertsMenu>
        </>
      )}
      {vitalsAlerts.length > 0 && !isMonitorNotAvailableAlertPresent(deviceAlerts) && (
        <>
          <Button
            data-testid='vitals-alerts-list'
            ref={targetRefVitals}
            onClick={handleClickVitals}
            sx={{
              ...buttonStyles,
              backgroundColor: getHighestPriorityAlertColor(vitalsAlerts),
              '&:hover': {
                backgroundColor: getHighestPriorityAlertColor(vitalsAlerts),
              },
            }}
          >
            <Typography variant='caption'>
              {getHighestPriorityAlertTitle(vitalsAlerts, ALERT_TYPES.VITALS)}
            </Typography>
            <Grid display='flex' flexDirection='row'>
              <NumberBadge
                number={vitalsAlerts.length}
                color={getHighestPriorityAlertColor(vitalsAlerts)}
              />
              <DownFullArrowIcon color={ALERT_TEXT_COLOR} />
            </Grid>
          </Button>
          <StyledAlertsMenu
            theme={theme}
            anchorEl={anchorElVitals}
            open={openVitals}
            onClose={handleCloseVitals}
            onClick={(event) => {
              event.stopPropagation();
            }}
            width={dimensions.width.toString() + 'px'}
            backgroundcolor='disabled'
            bordercolor={getHighestPriorityAlertColor(vitalsAlerts)}
          >
            {renderVitalsAlerts()}
          </StyledAlertsMenu>
        </>
      )}
    </Grid>
  );
};

export default AlertList;
