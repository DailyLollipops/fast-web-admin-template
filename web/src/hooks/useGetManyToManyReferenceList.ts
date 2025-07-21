import { useEffect, useState } from "react";
import { useDataProvider, useNotify } from "react-admin";

export function useGetManyToManyReferenceList<T>(
  resourcePath: [string, string],
  ids: string[],
  version?: number,
) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const dataProvider = useDataProvider();
  const notify = useNotify();

  useEffect(() => {
    setLoading(true);
    dataProvider
      .getManyToManyReferenceList(resourcePath, ids)
      .then((response: { data: T[] }) => {
        setData(response.data);
      })
      .catch((error: Error) => {
        notify(`Failed to load data: ${error.message}`, { type: "error" });
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [version]);

  return { data, loading };
}
