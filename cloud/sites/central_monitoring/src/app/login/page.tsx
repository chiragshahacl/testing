'use client';

import { useLogin } from '@/api/useLogin';
import LoginForm from '@/components/form/login';
import useSession from '@/hooks/useSession';
import { CopyrightText } from '@/styles/StyledComponents';
import { openSansFont } from '@/utils/fonts';
import { getCachedRuntimeConfig } from '@/utils/runtime';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { capitalize, truncate } from 'lodash';
import moment from 'moment';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { MutableRefObject, useEffect } from 'react';
import { FormReference, FormValues } from '@/types/form';
import { ServerErrorResponse } from '@/types/response';
import { getAuthErrorMessageKey } from '@/api/authErrors';
import useAudioManager from '@/hooks/useAudioManager';
import { USER_TYPE } from '@/constants';
import { useTranslation } from 'react-i18next';

/**
 * Handles user initial authentication flows
 */
const Login = () => {
  const router = useRouter();
  const { accessToken, refreshToken, authenticating, userType } = useSession();
  const { login } = useLogin();
  const { setAutoPlayActivated } = useAudioManager();
  const { t } = useTranslation();

  const version = getCachedRuntimeConfig().SIBEL_VERSION;

  useEffect(() => {
    // Redirects to home if authenticated
    if (!authenticating && accessToken && refreshToken && userType == USER_TYPE.NON_TECH) {
      router.replace('/home');
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
              router.replace('/home');
            }
          },
          onError: (err: ServerErrorResponse) => {
            if (formRef && formRef.current) {
              formRef.current.setErrors({
                password: t(getAuthErrorMessageKey(err)),
              });
            }
            setIsButtonDisabled(true);
          },
          onSettled: () => {
            if (formRef && formRef.current) {
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
      <Box className='radial-gradient' />
      <Grid
        container
        direction='column'
        alignItems='center'
        justifyContent='space-between'
        sx={{
          minHeight: '100vh',
          backdropFilter: 'brightness(80%)',
          padding: 16,
        }}
      >
        <Grid xs item display='flex' alignItems='flex-end'>
          <Image src='/loginLogo.png' width='106' height='120' alt='Logo' />
        </Grid>
        <Grid
          item
          sx={{
            flexDirection: 'column',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginY: 48.57,
            backgroundImage: 'url(/loginBg.svg)',
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover',
          }}
          className='border-gradient'
        >
          <Box sx={{ mb: 24 }}>
            <Typography variant='h1'>{t('LoginPage.title')}</Typography>
            <Box height={8} />
            <Typography
              fontFamily={openSansFont.style.fontFamily}
              color={(theme) => theme.palette.grey[600]}
              variant='subtitle1'
            >
              {t('LoginPage.subtitle')}
            </Typography>
          </Box>
          <Box>
            <LoginForm loginHandler={loginHandler} />
          </Box>
        </Grid>
        <Grid
          xs
          container
          item
          display='flex'
          direction='column'
          justifyContent='flex-end'
          alignItems='center'
        >
          <Image src='/sibelLogo.svg' width='107' height='30' alt='Sibel Logo' />
          <Box height={6} />
          <CopyrightText variant='body2' textAlign='center' data-testid='sibel-version'>
            {capitalize(truncate(version, { length: 24, omission: '...' }))}
          </CopyrightText>
          <CopyrightText variant='caption' textAlign='center'>
            {t('LoginPage.copyright', { year: moment().year().toString() })}
          </CopyrightText>
          <CopyrightText variant='caption' textAlign='center'>
            {t('LoginPage.UDI', {
              UDI: process.env.NEXT_PUBLIC_SIBEL_UDI + version.replace(/\D/g, ''),
            })}
          </CopyrightText>
        </Grid>
      </Grid>
    </>
  );
};

export default Login;
