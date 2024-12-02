import { disabledColor } from '@/constants';
import { openSansFont } from '@/utils/fonts';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';
import { get } from 'lodash';
import { ReactNode } from 'react';

interface VitalInfoComponentProps {
  hasAlert?: boolean;
  hasTechnicalAlert?: boolean;
  title?: string;
  subtitle: ReactNode;
  disabled?: boolean;
}

const VitalInfoComponent = ({
  hasAlert = false,
  hasTechnicalAlert = false,
  title,
  subtitle,
  disabled = false,
}: VitalInfoComponentProps) => {
  const theme = useTheme();
  return (
    <Box>
      {title ? (
        <Typography
          variant='h4'
          sx={{
            color: disabled
              ? disabledColor
              : hasTechnicalAlert
              ? get(theme.palette, 'alert.low')
              : hasAlert
              ? theme.palette.common.black
              : theme.palette.divider,
            marginBottom: 4,
          }}
        >
          {title}
        </Typography>
      ) : (
        <Box height={24} />
      )}
      <Typography
        variant='subtitle2'
        data-testid={`${String(title)}-subtitle`}
        sx={{
          fontFamily: openSansFont.style.fontFamily,
          color: disabled
            ? disabledColor
            : hasTechnicalAlert
            ? get(theme.palette, 'alert.low')
            : hasAlert
            ? theme.palette.common.black
            : theme.palette.divider,
          paddingBottom: 18,
        }}
      >
        {subtitle}
      </Typography>
    </Box>
  );
};

export default VitalInfoComponent;
