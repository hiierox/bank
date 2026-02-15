// Relative paths (/api/flow, /api/scoring) when behind proxy (Docker nginx or Vite dev proxy) — избегаем CORS
const flowUrl = import.meta.env.VITE_FLOW_URL ?? ''
const scoringUrl = import.meta.env.VITE_SCORING_URL ?? ''

export interface FlowProductsResponse {
  flow_type: 'pioneer' | 'repeater'
  available_products: Array<{ product_name: string; amount: number | string; percentage: number }>
}

export async function fetchFlowProducts(phone: string): Promise<FlowProductsResponse> {
  const base = flowUrl || '/api/flow'
  const res = await fetch(`${base}/api/products/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phone }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Flow: ${res.status}`)
  }
  return res.json()
}

export interface ScoringProductBody {
  name: string
  max_amount: number
  term_days: number
  interest_rate_daily: number
}

export interface ScoringResponse {
  decision: 'accepted' | 'rejected'
  product?: ScoringProductBody
}

export interface PioneerRequestBody {
  user_data: {
    phone: string
    age: number
    monthly_income: number
    employment_type: 'full_time' | 'freelance' | 'unemployed'
    has_property: boolean
  }
  products: ScoringProductBody[]
}

export async function scoringPioneer(body: PioneerRequestBody): Promise<ScoringResponse> {
  const base = scoringUrl || '/api/scoring'
  const res = await fetch(`${base}/api/scoring/pioneer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Scoring: ${res.status}`)
  }
  return res.json()
}

export interface RepeaterRequestBody {
  phone: string
  products: ScoringProductBody[]
}

export async function scoringRepeater(body: RepeaterRequestBody): Promise<ScoringResponse> {
  const base = scoringUrl || '/api/scoring'
  const res = await fetch(`${base}/api/scoring/repeater`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Scoring: ${res.status}`)
  }
  return res.json()
}
