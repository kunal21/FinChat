// reserved for types

export interface RouteInfo {
  userId: string;
}

export interface ItemType {
  id: number;
  plaid_item_id: string;
  user_id: number;
  plaid_access_token: string;
  plaid_institution_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AccountType {
  id: number;
  item_id: number;
  user_id: number;
  plaid_account_id: string;
  name: string;
  mask: string;
  official_name: string;
  current_balance: number;
  available_balance: number;
  iso_currency_code: string;
  unofficial_currency_code: string;
  type: 'depository' | 'investment' | 'loan' | 'credit';
  subtype:
    | 'checking'
    | 'savings'
    | 'cd'
    | 'money market'
    | 'ira'
    | '401k'
    | 'student'
    | 'mortgage'
    | 'credit card';
  created_at: string;
  updated_at: string;
}
export interface TransactionType {
  id: number;
  account_id: number;
  item_id: number;
  user_id: number;
  plaid_transaction_id: string;
  plaid_category_id: string;
  category: string;
  personal_finance_category_primary: string;
  personal_finance_category_detailed: string;
  type: string;
  name: string;
  amount: number;
  iso_currency_code: string;
  unofficial_currency_code: string;
  date: string;
  pending: boolean;
  account_owner: string;
  created_at: string;
  updated_at: string;
}

export interface AssetType {
  id: number;
  user_id: number;
  value: number;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface HoldingType {
  id: number;
  account_id: number;
  plaid_account_id: string;
  security_id: string;
  name: string;
  ticker_symbol: string | null;
  security_type: string | null;
  quantity: number | null;
  institution_price: number | null;
  institution_price_as_of: string | null;
  institution_value: number | null;
  cost_basis: number | null;
  iso_currency_code: string | null;
  unofficial_currency_code: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserType {
  id: number;
  username: string | null;
  created_at: string;
  updated_at: string;
}

export interface MessageType {
  id: number;
  user_id: number;
  text: string;
  createdAt: string;
  updatedAt: string;
  author: string; // bot or user
}
