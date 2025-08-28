import {
  fetchUtils,
  DataProvider,
  withLifecycleCallbacks,
  CreateParams,
} from "react-admin";
import { stringify } from "query-string";
import { AUTH_KEY, API_URL } from "../constants";
import { alternateJoin } from "../utils";

const httpClient = (
  url: string,
  options: fetchUtils.Options | undefined = {},
) => {
  const token = localStorage.getItem(AUTH_KEY);
  options.headers = new Headers(options.headers || {});
  if (token) {
    options.headers.set("Authorization", `Bearer ${token}`);
  }
  return fetchUtils.fetchJson(url, options);
};

export const dataProvider: DataProvider = withLifecycleCallbacks(
  {
    getList: async (resource, params) => {
      const orderField = params.sort?.field;
      const orderBy = params.sort?.order;
      const page = params.pagination?.page;
      const perPage = params.pagination?.perPage;
      const isInfinite = params.meta?.infinite === true;

      const query: Record<string, string> = {};

      if (orderField !== undefined) {
        query["order_field"] = orderField.toLowerCase();
      }
      if (orderBy !== undefined) {
        query["order_by"] = orderBy.toLowerCase();
      }
      if (!isInfinite && page !== undefined && perPage !== undefined) {
        query["offset"] = ((page - 1) * perPage).toString();
        query["limit"] = perPage.toString();
      }
      if (params.filter !== undefined) {
        const operators = {
          _neq: "!=",
          _gt: ">",
          _gte: ">=",
          _lt: "<",
          _lte: "<=",
          _in: "in",
          _nin: "not_in",
          _ilike: "ilike",
          _like: "like",
        };

        const filters = Object.keys(params.filter).map((key) => {
          const matchedOp = Object.entries(operators).find(([suffix]) =>
            key.endsWith(suffix),
          );
          return matchedOp
            ? {
                field: key.slice(0, -matchedOp[0].length),
                operator: matchedOp[1],
                value: params.filter[key],
              }
            : {
                field: key,
                operator: "==",
                value: params.filter[key],
              };
        });

        query["filters"] = JSON.stringify(filters);
      }

      const url = `${API_URL}/${resource}?${stringify(query)}`;
      const { json } = await httpClient(url, { signal: params.signal });

      return {
        data: json.data,
        total: json.total,
      };
    },

    getOne: async (resource, params) => {
      const url = `${API_URL}/${resource}/${params.id}`;
      const { json } = await httpClient(url, { signal: params.signal });
      return { data: json };
    },

    getMany: async (resource, params) => {
      const query = {
        filter: JSON.stringify({ ids: params.ids }),
      };
      const url = `${API_URL}/${resource}?${stringify(query)}`;
      const { json } = await httpClient(url, { signal: params.signal });
      return { data: json };
    },

    getManyReference: async (resource, params) => {
      const orderField = params.sort?.field;
      const orderBy = params.sort?.order;
      const page = params.pagination?.page;
      const perPage = params.pagination?.perPage;

      const query: Record<string, string> = {};

      if (orderField !== undefined) {
        query["order_field"] = orderField;
      }
      if (orderBy !== undefined) {
        query["order_by"] = orderBy.toLowerCase();
      }
      if (page !== undefined && perPage !== undefined) {
        query["offset"] = ((page - 1) * perPage).toString();
        query["limit"] = perPage.toString();
      }
      if (params.filter !== undefined) {
        const filters = params.filter;
        filters[`${params.target}`] = params.id;
        query["filters"] = JSON.stringify(filters);
      }

      const url = `${API_URL}/${resource}?${stringify(query)}`;
      const { json } = await httpClient(url, { signal: params.signal });

      return {
        data: json.data,
        total: json.total,
      };
    },

    create: async (resource, params) => {
      const { json } = await httpClient(`${API_URL}/${resource}`, {
        method: "POST",
        body: JSON.stringify(params.data),
      });
      return { data: json };
    },

    update: async (resource, params) => {
      const url = `${API_URL}/${resource}/${params.id}`;
      const { json } = await httpClient(url, {
        method: "PATCH",
        body: JSON.stringify(params.data),
      });
      return { data: json };
    },

    updateMany: async (resource, params) => {
      const query = {
        filter: JSON.stringify({ id: params.ids }),
      };
      const url = `${API_URL}/${resource}?${stringify(query)}`;
      const { json } = await httpClient(url, {
        method: "PATCH",
        body: JSON.stringify(params.data),
      });
      return { data: json };
    },

    delete: async (resource, params) => {
      const url = `${API_URL}/${resource}/${params.id}`;
      const { json } = await httpClient(url, {
        method: "DELETE",
      });
      return { data: json };
    },

    deleteMany: async (resource, params) => {
      const query = {
        filter: JSON.stringify({ id: params.ids }),
      };
      const url = `${API_URL}/${resource}?${stringify(query)}`;
      const { json } = await httpClient(url, {
        method: "DELETE",
      });
      return { data: json };
    },

    getManyToManyReferenceList: async (resources: string[], ids: string[]) => {
      const url = `${API_URL}/${alternateJoin(resources, ids)}`;
      const { json } = await httpClient(url, {
        method: "GET",
      });

      return {
        data: json.data,
        total: json.total,
      };
    },

    getManyToManyReferenceOne: async (resources: string[], ids: string[]) => {
      const url = `${API_URL}/${alternateJoin(resources, ids)}`;
      const { json } = await httpClient(url, {
        method: "GET",
      });

      return { data: json };
    },

    createManyToManyReference: async (
      resources: string[],
      ids: string[],
      params: CreateParams,
    ) => {
      const url = `${API_URL}/${alternateJoin(resources, ids)}`;
      const { json } = await httpClient(url, {
        method: "POST",
        body: JSON.stringify(params.data),
      });
      return { data: json };
    },

    deleteManyToManyReference: async (resources: string[], ids: string[]) => {
      const url = `${API_URL}/${alternateJoin(resources, ids)}`;
      const { json } = await httpClient(url, {
        method: "DELETE",
      });

      return { data: json };
    },

    fetchJson: async (
      url: string,
      options: fetchUtils.Options | undefined = {},
    ) => {
      const fullUrl = `${API_URL}${url}`;
      return await httpClient(fullUrl, options);
    },
  },
  [
    // Add lifecycle callbacks here
  ],
);
