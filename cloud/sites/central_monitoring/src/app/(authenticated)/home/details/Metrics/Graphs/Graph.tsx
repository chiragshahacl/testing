import AlertGraphCard from '@/components/cards/AlertGraphCard';
import GraphCard, { SHOW_TEXT } from '@/components/graph/GraphCard';
import GraphTitle from '@/components/graph/GraphTitle';
import { BedType } from '@/types/bed';
import { ChartType } from '@/types/charts';
import { Sensor } from '@/types/sensor';
import { getAlertColor } from '@/utils/alertUtils';
import { getPLETHGraphRelatedSensor } from '@/utils/graphUtils';
import { ALERT_PRIORITY } from '@/utils/metricCodes';
import Grid from '@mui/material/Grid';
import { Theme, alpha } from '@mui/material/styles';
import { get } from 'lodash';
import { XyDataSeries } from 'scichart';

type GraphProps = {
  alertPriority?: ALERT_PRIORITY;
  alertMessage?: string;
  bed: BedType;
  onUpdate: (dataSeries?: XyDataSeries) => void;
  hasData: boolean;
  color: string;
  chartType: ChartType;
  height: number;
  activeSensors?: Sensor[];
};
const Graph = ({
  alertPriority,
  alertMessage,
  bed,
  hasData,
  onUpdate,
  color,
  chartType,
  height,
  activeSensors,
}: GraphProps) => {
  return (
    <Grid flex={5} mr={8} position='relative'>
      <GraphTitle sx={{ color: (theme: Theme) => get(theme.palette, color) as string }}>
        {chartType.toUpperCase()}
      </GraphTitle>
      {alertPriority ? (
        <AlertGraphCard
          priority={alertPriority}
          alertMessage={alertMessage}
          height={height}
          textBg='primary.dark'
          styles={{
            backgroundColor: getAlertColor(alertPriority)
              ? alpha(getAlertColor(alertPriority) || '', 0.25)
              : 'primary.dark',
            minHeight: '100%',
          }}
        />
      ) : (
        <GraphCard
          key={`${chartType}_${bed?.patient?.patientPrimaryIdentifier || ''}`}
          bedData={bed}
          hasDataLoaded={hasData}
          chartType={chartType}
          showText={SHOW_TEXT.METRIC_NAME}
          maxHeight={height}
          elementId={`pid_${bed?.patient?.patientPrimaryIdentifier || ''}_${chartType}`}
          sendUpdateCallback={(_, dataSeries) => onUpdate(dataSeries)}
          hasActivePatientSession
          showScale={chartType === ChartType.ECG}
          sensorType={
            activeSensors && chartType === ChartType.PLETH
              ? getPLETHGraphRelatedSensor(activeSensors)
              : undefined
          }
        />
      )}
    </Grid>
  );
};

export default Graph;
