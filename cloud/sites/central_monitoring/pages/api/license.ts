/* eslint-disable camelcase */

import { NextApiRequest, NextApiResponse } from 'next';
import { DataType, open, define } from 'ffi-rs';
import path from 'path';
import os from 'os';

const getMachineType = (): string => {
  switch (os.machine()) {
    case 'arm':
      return 'arm';
    case 'arm64':
      return 'arm64';
    case 'aarch64':
      return 'arm64';
    case 'i386':
      return 'x86';
    case 'x86_64':
    case 'i686':
      return 'x64';
    default:
      throw new Error(`Unsupported machine type: ${os.machine()}`);
  }
};

const getArchitecture = (): string => {
  switch (os.platform()) {
    case 'aix':
    case 'darwin':
    case 'freebsd':
    case 'linux':
    case 'openbsd':
    case 'sunos':
      return 'linux';
    case 'win32':
      return 'win32';
    default:
      throw new Error(`Unsupported architecture: ${os.platform()}`);
  }
};

const getFilename = (arch: string): string => {
  switch (arch) {
    case 'win32':
      return 'SciChartLicenseServer.dll';
    case 'linux':
      return 'libSciChartLicenseServer.so';
    default:
      throw new Error(`Unsupported architecture: ${arch}`);
  }
};

const getRuntimeLibraryFolder = (): string => {
  const machineType = getMachineType();
  const architecture = getArchitecture();
  const fileName = getFilename(architecture);

  const libraryName = `${architecture}-${machineType}/native/${fileName}`;

  const libraryPath = path.join(path.dirname(__dirname), 'runtimes', libraryName);

  return libraryPath;
};

const library = 'SciChartLicenseServer';

const libraryPath = getRuntimeLibraryFolder();

// Open the dynamic library: TODO: open library in macOS
open({ library, path: libraryPath });

// Configure the native api
const nativeLicenseServer = define({
  SciChartLicenseServer_SetAssemblyName: {
    library,
    // @ts-ignore: Ignore the type error for this line
    retType: DataType.Boolean,
    // @ts-ignore: Ignore the type error for this line
    paramsType: [DataType.String],
  },
  SciChartLicenseServer_SetRuntimeLicenseKey: {
    library,
    // @ts-ignore: Ignore the type error for this line
    retType: DataType.Boolean,
    // @ts-ignore: Ignore the type error for this line
    paramsType: [DataType.String],
  },
  SciChartLicenseServer_ValidateChallenge: {
    library,
    // @ts-ignore: Ignore the type error for this line
    retType: DataType.String,
    // @ts-ignore: Ignore the type error for this line
    paramsType: [DataType.String],
  },
  SciChartLicenseServer_Dump: {
    library,
    // @ts-ignore: Ignore the type error for this line
    retType: DataType.String,
    paramsType: [],
  },
  SciChartLicenseServer_GetLicenseErrors: {
    library,
    // @ts-ignore: Ignore the type error for this line
    retType: DataType.String,
    paramsType: [],
  },
});

nativeLicenseServer.SciChartLicenseServer_SetAssemblyName(['cms']);

// Set the Server key
nativeLicenseServer.SciChartLicenseServer_SetRuntimeLicenseKey([process.env.SCI_CHART_SERVER_KEY]);

// eslint-disable-next-line no-empty-pattern
const handler = (req: NextApiRequest, res: NextApiResponse) => {
  if (req.url && req.headers.host) {
    // Extract properties from NextApiRequest
    if (!req.query.challenge) {
      res.status(403).end();
    } else {
      const challenge = req.query.challenge.toString();
      const result = nativeLicenseServer.SciChartLicenseServer_ValidateChallenge([challenge]);
      res.status(200).send(result);
    }
  }
  res.status(400).end();
};
export default handler;
