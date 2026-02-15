/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FLOW_URL: string
  readonly VITE_SCORING_URL: string
  readonly VITE_DATA_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
