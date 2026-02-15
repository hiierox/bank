import { useState } from 'react'
import {
  fetchFlowProducts,
  scoringPioneer,
  scoringRepeater,
  type FlowProductsResponse,
  type ScoringResponse,
} from './api'
import { flowProductsToScoring, type FlowProduct } from './productMapping'
import './App.css'

const PHONE_REG = /^7\d{10}$/

type Step = 1 | 2 | 3

export default function App() {
  const [phone, setPhone] = useState('')
  const [flow, setFlow] = useState<FlowProductsResponse | null>(null)
  const [step, setStep] = useState<Step>(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Pioneer form
  const [age, setAge] = useState(25)
  const [monthlyIncome, setMonthlyIncome] = useState(50000)
  const [employmentType, setEmploymentType] = useState<'full_time' | 'freelance' | 'unemployed'>('full_time')
  const [hasProperty, setHasProperty] = useState(false)
  const [selectedProductIndex, setSelectedProductIndex] = useState(0)

  const [scoringResult, setScoringResult] = useState<ScoringResponse | null>(null)

  const rawProducts = flow?.available_products
  const availableProducts = Array.isArray(rawProducts) ? rawProducts : []
  const flowType = flow?.flow_type ?? null
  const productsForScoring =
    flowType && availableProducts.length > 0
      ? flowProductsToScoring(
          availableProducts as FlowProduct[],
          flowType
        )
      : []

  const handleFetchFlow = async () => {
    const trimmed = phone.trim()
    if (!PHONE_REG.test(trimmed)) {
      setError('Телефон: 11 цифр, начинается с 7 (например 79001234567)')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const res = await fetchFlowProducts(trimmed)
      setFlow(res)
      setStep(2)
      setSelectedProductIndex(0)
      setScoringResult(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка запроса')
    } finally {
      setLoading(false)
    }
  }

  const handleScoring = async () => {
    if (!flow || !flowType || productsForScoring.length === 0) return
    const product = productsForScoring[selectedProductIndex]
    if (!product) return

    setError(null)
    setLoading(true)
    setScoringResult(null)
    try {
      if (flowType === 'pioneer') {
        const res = await scoringPioneer({
          user_data: {
            phone: phone.trim(),
            age,
            monthly_income: monthlyIncome,
            employment_type: employmentType,
            has_property: hasProperty,
          },
          products: [product],
        })
        setScoringResult(res)
      } else {
        const res = await scoringRepeater({
          phone: phone.trim(),
          products: [product],
        })
        setScoringResult(res)
      }
      setStep(3)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка скоринга')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setFlow(null)
    setStep(1)
    setScoringResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <main className="main">
        <h1 style={{ marginTop: 0 }}>Демо: Скоринг</h1>

        {/* Step 1 */}
        <section className="step">
          <h2>Шаг 1 — Телефон</h2>
          <p>Введите номер (7XXXXXXXXXX), чтобы определить тип флоу.</p>
          <input
            type="text"
            placeholder="79001234567"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            disabled={!!flow}
            maxLength={11}
          />
          {!flow && (
            <button onClick={handleFetchFlow} disabled={loading}>
              {loading ? 'Загрузка…' : 'Определить флоу'}
            </button>
          )}
          {flow && (
            <>
              <span className={`flow-badge ${flowType ?? ''}`}>
                {flowType === 'pioneer' ? 'Pioneer' : 'Repeater'}
              </span>
              <button onClick={reset} type="button">
                Сбросить
              </button>
            </>
          )}
        </section>

        {/* Step 2 */}
        {flow && step >= 2 && (
          <section className="step">
            <h2>Шаг 2 — Данные и выбор кредита</h2>

            {flowType === 'pioneer' && (
              <>
                <label>Возраст</label>
                <input
                  type="number"
                  min={18}
                  max={120}
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                />
                <label>Зарплата (руб/мес)</label>
                <input
                  type="number"
                  min={1}
                  value={monthlyIncome}
                  onChange={(e) => setMonthlyIncome(Number(e.target.value))}
                />
                <label>Занятость</label>
                <select
                  value={employmentType}
                  onChange={(e) =>
                    setEmploymentType(e.target.value as 'full_time' | 'freelance' | 'unemployed')
                  }
                >
                  <option value="full_time">Полная занятость</option>
                  <option value="freelance">Фриланс</option>
                  <option value="unemployed">Без работы</option>
                </select>
                <label className="inline">
                  <input
                    type="checkbox"
                    checked={hasProperty}
                    onChange={(e) => setHasProperty(e.target.checked)}
                  />
                  Есть недвижимость
                </label>
              </>
            )}

            <label>Выберите кредит</label>
            <select
              value={selectedProductIndex}
              onChange={(e) => setSelectedProductIndex(Number(e.target.value))}
            >
              {availableProducts.map((p, i) => (
                <option key={i} value={i}>
                  {p.product_name} — {p.amount} ₽, {p.percentage}%
                </option>
              ))}
            </select>

            <p>
              <button onClick={handleScoring} disabled={loading}>
                {loading ? 'Отправка…' : 'Отправить на скоринг'}
              </button>
            </p>
          </section>
        )}

        {/* Step 3 result */}
        {step >= 3 && scoringResult && (
          <section className="step">
            <h2>Результат скоринга</h2>
            <div
              className={`result-box ${
                scoringResult.decision === 'accepted' ? 'accepted' : 'rejected'
              }`}
            >
              {scoringResult.decision === 'accepted' ? (
                <>
                  <span className="success">Одобрено</span>
                  {scoringResult.product && (
                    <div className="product-name">
                      {scoringResult.product.name} — до {scoringResult.product.max_amount} ₽
                    </div>
                  )}
                </>
              ) : (
                <>
                  <span>Отказ</span>
                  {flowType === 'pioneer' && (
                    <div style={{ marginTop: 8, fontSize: '0.9rem', opacity: 0.9 }}>
                      Для pioneer отказ также возможен при лимите: более 3 попыток в сутки.
                    </div>
                  )}
                </>
              )}
            </div>
          </section>
        )}

        {error && <p className="error">{error}</p>}
      </main>

      {/* Debug sidebar */}
      <aside className="sidebar">
        <h3>Отладка</h3>
        {flow ? (
          <>
            <div>
              <strong>Доступные кредиты для флоу</strong>
              <ul className="product-list">
                {availableProducts.map((p, i) => (
                  <li key={i}>
                    {p.product_name} — {String(p.amount)} ₽, {p.percentage}%
                  </li>
                ))}
              </ul>
            </div>
            {scoringResult && (
              <div>
                <strong>Результат скоринга</strong>
                <pre>{JSON.stringify(scoringResult, null, 2)}</pre>
              </div>
            )}
          </>
        ) : (
          <p style={{ color: '#64748b', fontSize: '0.85rem' }}>
            Введите телефон и нажмите «Определить флоу» — здесь появится список доступных кредитов.
          </p>
        )}
      </aside>
    </div>
  )
}
