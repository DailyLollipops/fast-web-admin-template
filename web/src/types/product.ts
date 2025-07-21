export interface Product {
  id: number;
  name: string;
  description: string;
  image: string;
  remaining: number | undefined;
  last_sale: number | undefined;
  last_price: number | undefined;
}
