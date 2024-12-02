import { useSearchParams } from 'next/navigation';
import { z } from 'zod';

const searchParamsSchema = z.object({
  groupIndex: z.coerce.number().optional(),
  hideSetup: z.coerce.number().optional(),
});

const useTypedSearchParams = () => {
  const searchParams = useSearchParams();

  if (!searchParams) return {};

  const searchParamsObject = Object.fromEntries(searchParams.entries());

  const validatedSearchParams = searchParamsSchema.safeParse(searchParamsObject);

  if (!validatedSearchParams.success) return {};

  return validatedSearchParams.data;
};

export default useTypedSearchParams;
