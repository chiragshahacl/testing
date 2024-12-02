/* eslint-disable quotes */

import { NextResponse } from 'next/server';
// eslint-disable-next-line no-duplicate-imports
import type { NextRequest } from 'next/server';

const getPageUrls = () => {
  return process.env.CMS_URLS;
};

const getAPIUrls = () => {
  return process.env.APP_URL;
};

const getWSUrls = () => {
  return `${process.env.WSS_URL} ${process.env.CMS_WSS_URLS}`;
};

const CSPAttributes = {
  // @debt: Remove unsafe values. Temprary until we have functionalities ironed out
  'script-src': "script-src self 'unsafe-eval'",
  // @debt: Remove unsafe value. Temporary until design is finalized
  'style-src': `style-src 'unsafe-inline' ${getPageUrls()}`,
  'connect-src': `connect-src ${getPageUrls()} ${getAPIUrls()} ${getWSUrls()} https://cdn.jsdelivr.net`,
  // @debt: remove unsafe value. Temporary until functionalities are ironed out
  'script-src-elem': `script-src-elem 'unsafe-inline' ${getPageUrls()}`,
  'worker-src': `worker-src 'self' ${getPageUrls()}`,
};
const CSPValue = Object.values(CSPAttributes).join('; ');

// This function can be marked `async` if using `await` inside
export function middleware(request: NextRequest) {
  const requestHeaders = new Headers(request.headers);

  requestHeaders.set('Content-Security-Policy', CSPValue);

  const response = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
  response.headers.set('Content-Security-Policy', CSPValue);
  return response;
}
