/**
 * Маппинг продукта из flow (product_name, amount, percentage)
 * в формат scoring (name, max_amount, term_days, interest_rate_daily).
 * term_days и interest_rate_daily берём из констант бэкенда (mock/constants).
 */
export interface FlowProduct {
  product_name: string
  amount: number | string
  percentage: number
}

export interface ScoringProduct {
  name: string
  max_amount: number
  term_days: number
  interest_rate_daily: number
}

const PIONEER_EXTRA: Record<string, { term_days: number; interest_rate_daily: number }> = {
  MicroLoan: { term_days: 30, interest_rate_daily: 1.0 },
  QuickMoney: { term_days: 60, interest_rate_daily: 0.8 },
  ConsumerLoan: { term_days: 90, interest_rate_daily: 0.5 },
}

const REPEATER_EXTRA: Record<string, { term_days: number; interest_rate_daily: number }> = {
  LoyaltyLoan: { term_days: 100, interest_rate_daily: 0.4 },
  AdvantagePlus: { term_days: 120, interest_rate_daily: 0.3 },
  PrimeCredit: { term_days: 180, interest_rate_daily: 0.2 },
}

export function flowProductToScoring(
  p: FlowProduct,
  flowType: 'pioneer' | 'repeater'
): ScoringProduct {
  const extra = flowType === 'pioneer' ? PIONEER_EXTRA[p.product_name] : REPEATER_EXTRA[p.product_name]
  const term_days = extra?.term_days ?? 30
  const interest_rate_daily = extra?.interest_rate_daily ?? 0.5
  const raw = p.amount
  const max_amount = typeof raw === 'string' ? parseInt(raw, 10) : Number(raw)
  return {
    name: p.product_name,
    max_amount: Number.isNaN(max_amount) ? 0 : max_amount,
    term_days,
    interest_rate_daily,
  }
}

export function flowProductsToScoring(
  products: FlowProduct[],
  flowType: 'pioneer' | 'repeater'
): ScoringProduct[] {
  return products.map((p) => flowProductToScoring(p, flowType))
}
