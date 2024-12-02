'use client';

import { useTechnicalLogin } from '@/api/useLogin';
import LoginForm from '@/components/form/login';
import { CopyrightText } from '@/styles/StyledComponents';
import { FormReference, FormValues } from '@/types/form';
import { getCachedRuntimeConfig } from '@/utils/runtime';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { capitalize, truncate } from 'lodash';
import moment from 'moment';
import Image from 'next/image';
import { MutableRefObject, useEffect } from 'react';
import useAudioManager from '@/hooks/useAudioManager';
import { useRouter } from 'next/navigation';
import { ServerErrorResponse } from '@/types/response';
import { getAuthErrorMessage } from '@/api/authErrors';
import { ACTIVE_SESSION_KEY, USER_TYPE } from '@/constants';
import useSession from '@/hooks/useSession';

const TechnicalLogin = () => {
  const router = useRouter();
  const { accessToken, refreshToken, authenticating, userType } = useSession();
  const { setAutoPlayActivated } = useAudioManager();
  const { login } = useTechnicalLogin();

  const version = getCachedRuntimeConfig().SIBEL_VERSION;

  useEffect(() => {
    // Redirects to home if authenticated
    if (
      !authenticating &&
      accessToken &&
      refreshToken &&
      userType == USER_TYPE.TECH &&
      sessionStorage.getItem(ACTIVE_SESSION_KEY) === 'true'
    ) {
      router.replace('/technical/home');
    }
  }, [accessToken, authenticating, refreshToken, router, userType]);

  const loginHandler = async (
    values: FormValues,
    formRef: MutableRefObject<FormReference | null>,
    setIsButtonDisabled: (state: boolean) => void
  ) => {
    if (formRef != null && formRef.current != null) {
      setAutoPlayActivated(true);
      await login(
        { password: values.password },
        {
          onSuccess: () => {
            if (formRef && formRef.current) {
              formRef.current.setStatus({ success: true });
              router.replace('/technical/home');
            }
          },
          onError: (err: ServerErrorResponse) => {
            if (formRef && formRef.current) {
              formRef.current.setErrors({
                password: getAuthErrorMessage(err),
              });
            }
            setIsButtonDisabled(true);
          },
          onSettled: () => {
            if (formRef && formRef.current) {
              sessionStorage.setItem(ACTIVE_SESSION_KEY, 'true');
              formRef.current.setSubmitting(false);
            }
          },
        }
      );
    }
  };

  return (
    <>
      <title>CMS - Login</title>
      <Grid
        display='flex'
        flexDirection='column'
        alignItems='center'
        justifyContent='center'
        gap={40.2}
        sx={{
          height: '100vh',
          backgroundColor: 'primary.dark',
        }}
      >
        <Image src='/ANNE_IT_LoginLogo.png' width='106' height='120' alt='Logo' />
        <Grid
          display='flex'
          flexDirection='column'
          gap={24}
          sx={{
            backgroundImage: 'url(/itBg.svg)',
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover',
            marginBottom: 106,
          }}
          className='border-gradient'
        >
          <Typography variant='h1'>Log in</Typography>
          <LoginForm loginHandler={loginHandler} />
        </Grid>
        <Grid
          display='flex'
          flexDirection='column'
          alignItems='center'
          position='absolute'
          bottom={0}
        >
          <Image src='/sibelLogo.svg' width='107' height='30' alt='Sibel Logo' />
          <Box height={4} />
          <CopyrightText variant='body2' textAlign='center' data-testid='sibel-version'>
            {capitalize(truncate(version, { length: 24, omission: '...' }))}
          </CopyrightText>
          <CopyrightText sx={{}} variant='caption' textAlign='center'>
            {`Copyright © ${moment().year()} Sibel Inc. All rights reserved.`}
          </CopyrightText>
          <CopyrightText variant='caption' textAlign='center'>
            {`UDI: ${process.env.NEXT_PUBLIC_SIBEL_UDI + version.replace(/\D/g, '')}`}
          </CopyrightText>
        </Grid>
      </Grid>
    </>
  );
};

export default TechnicalLogin;
