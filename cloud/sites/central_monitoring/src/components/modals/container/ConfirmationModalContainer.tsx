import { StyledModalContainer } from '@/styles/StyledComponents';
import Typography from '@mui/material/Typography';
import React, { ForwardedRef, ReactNode } from 'react';

interface ConfirmationModalContainerProps {
  title: string;
  description: string;
  children: ReactNode;
}

const ConfirmationModalContainer = React.forwardRef(
  (
    { title, description, children }: ConfirmationModalContainerProps,
    ref: ForwardedRef<HTMLDivElement>
  ) => {
    return (
      <StyledModalContainer
        ref={ref}
        container
        item
        lg={5}
        sx={{
          flexDirection: 'column',
        }}
      >
        <Typography variant='h1'>{title}</Typography>
        <Typography variant='subtitle1' sx={{ marginY: 24 }}>
          {description}
        </Typography>
        {children}
      </StyledModalContainer>
    );
  }
);

ConfirmationModalContainer.displayName = 'ConfirmationModalContainer';

export default ConfirmationModalContainer;
