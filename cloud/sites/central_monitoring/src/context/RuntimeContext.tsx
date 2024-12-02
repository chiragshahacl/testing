import axios from 'axios';
import { ReactNode, createContext, useEffect, useState } from 'react';
import { RuntimeConfig, getCachedRuntimeConfig, setCachedRuntimeConfig } from '../utils/runtime';

export interface Props {
  children: ReactNode;
}
export const RuntimeConfigContext = createContext<RuntimeConfig | null>(null);

const RuntimeConfigProvider = ({ children }: Props) => {
  const [runtimeConfig, setRuntimeConfig] = useState(getCachedRuntimeConfig());

  useEffect(() => {
    // Updates the local config depending on sent values from local Next API
    if (global.window) {
      const execute = async () => {
        try {
          const response = await axios.get<RuntimeConfig>(`${window.location.origin}/api/user`);
          if (response.status === 200) {
            if (!runtimeConfig || JSON.stringify(response.data) !== JSON.stringify(runtimeConfig)) {
              setRuntimeConfig(response.data);
              setCachedRuntimeConfig(response.data);
            }
          }
        } catch (e) {
          /* empty */
        }
      };
      void execute();
    }
  }, [runtimeConfig]);

  return (
    <RuntimeConfigContext.Provider value={runtimeConfig}>{children}</RuntimeConfigContext.Provider>
  );
};
export default RuntimeConfigProvider;
