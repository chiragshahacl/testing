import Loading from '@/app/loading';
import CloseIcon from '@/components/icons/CloseIcon';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { alpha, styled } from '@mui/material/styles';
import React, { ReactElement } from 'react';

const Container = styled(Grid)((props) => ({
  display: props.hidden ? 'none' : 'flex',
  visibility: props.hidden ? 'hidden' : 'visible',
  position: 'absolute',
  top: 0,
  bottom: 0,
  left: 0,
  right: 0,
  backgroundColor: alpha(props.theme.palette.common.black, 0.5),
  zIndex: 1300,
}));

const Dialog = styled(Grid)(({ theme }) => ({
  display: 'flex',
  backgroundColor: theme.palette.primary.dark,
  justifyContent: 'center',
  flexDirection: 'column',
  padding: 16,
  borderRadius: 16,
  margin: 'auto',
  width: 1200,
  height: 800,
  gap: 24,
}));

const Header = styled(Grid)(() => ({
  display: 'flex',
  justifyContent: 'space-between',
}));

const Body = styled(Grid)(() => ({
  display: 'flex',
  flexDirection: 'row',
  gap: 16,
  height: 624,
}));

interface ModalContainerProps {
  headerTitle: string;
  headerIcon?: ReactElement;
  footer?: ReactElement;
  children: React.ReactNode;
  modalHidden?: boolean;
  onClose: () => void;
  dismissable?: boolean;
  loading?: boolean;
}

const ModalContainer = ({
  headerTitle,
  headerIcon = undefined,
  footer = undefined,
  children,
  modalHidden = false,
  onClose,
  dismissable = true,
  loading = false,
}: ModalContainerProps) => {
  return (
    <Container hidden={modalHidden} data-testid={`${headerTitle}-modal`}>
      <Dialog>
        {loading ? (
          <Loading height='auto' />
        ) : (
          <>
            <Header>
              <Grid item display='flex'>
                {headerIcon}
                <Typography variant='h2'>{headerTitle}</Typography>
              </Grid>
              {dismissable && <CloseIcon handleClick={onClose} />}
            </Header>
            <Body>{children}</Body>
            {footer}
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default ModalContainer;
