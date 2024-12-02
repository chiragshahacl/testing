import moment from 'moment';

const getExpFromJWTToken = (token: string): number => {
  return (
    JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()) as Record<
      string,
      string | number
    >
  ).exp as number;
};

/**
 * Checks if passed token is valid or has expired
 */
export const isTokenValid = (token: string) => {
  const expireTime = getExpFromJWTToken(token) * 1000; // Tokens from server are in seconds so we multiply by 1000
  return moment.utc(expireTime).isAfter(moment.now());
};
