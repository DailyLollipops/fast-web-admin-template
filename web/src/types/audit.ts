export interface Audit {
  id: number;
  user_id: number;
  branch_id: number;
  machine_id: string;
  product_id: string;
  remaining: number;
  dispensed: number;
  expenses: number;
  price: number;
  sales: number;
  refill_amount: number;
  category: string;
  created_at: string;
  updated_at: string;
}
