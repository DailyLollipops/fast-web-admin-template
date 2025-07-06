import { fetchUtils, DataProvider } from "react-admin";
import { stringify } from "query-string";
import { AUTH_KEY, API_URL } from "./constants";

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

export const dataProvider: DataProvider = {
  getList: async (resource, params) => {
    const orderField = params.sort?.field;
    const orderBy = params.sort?.order;
    const page = params.pagination?.page;
    const perPage = params.pagination?.perPage;

    const query: Record<string, string> = {};

    if (orderField !== undefined) {
      query["order_field"] = orderField.toLowerCase();
    }
    if (orderBy !== undefined) {
      query["order_by"] = orderBy.toLowerCase();
    }
    if (page !== undefined && perPage !== undefined) {
      query["offset"] = ((page - 1) * perPage).toString();
      query["limit"] = perPage.toString();
    }
    if (params.filter !== undefined) {
      query["filters"] = JSON.stringify(params.filter);
    }

    const url = `${API_URL}/${resource}?${stringify(query)}`;

    const { json } = await httpClient(url, { signal: params.signal });
    const data = json as Array<
      Record<string, string | number | boolean | null>
    >;
    return {
      data: json,
      total: data.length,
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
      query["order_by"] = orderBy;
    }
    if (page !== undefined && perPage !== undefined) {
      query["offset"] = ((page - 1) * perPage).toString();
      query["limit"] = perPage.toString();
    }
    if (params.filter !== undefined) {
      query["filters"] = JSON.stringify(params.filter);
    }

    const url = `${API_URL}/${resource}?${stringify(query)}`;

    const { json, headers } = await httpClient(url, { signal: params.signal });

    const contentRange = headers.get("content-range");
    if (!contentRange) {
      throw new Error('The "content-range" header is missing in the response.');
    }

    const total = parseInt(contentRange.split("/").pop() ?? "0", 10);

    return {
      data: json,
      total,
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
};
