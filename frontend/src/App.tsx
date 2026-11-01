
import { useRef, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import './App.css'
import './RAG.css'

type IconName =
  | 'grid'
  | 'files'
  | 'search'
  | 'message'
  | 'settings'
  | 'help'
  | 'upload'
  | 'shield'
  | 'clock'
  | 'arrow'
  | 'file'
  | 'sparkles'
  | 'menu'
  | 'check'
  | 'close'

type UploadResponse = {
  document_id: string
  filename: string
  page_count: number
  size_bytes: number
  status: string
  message: string
}



type SummaryParty = {
  name: string
  role: string
}

type SummaryKeyDate = {
  event: string
  date: string | null
  page_numbers: string[]
  citation_status?: string
}

type SummaryPaymentTerm = {
  term: string
  details: string
  page_numbers: string[]
  citation_status?: string
}

type SummaryObligation = {
  party: string
  obligation: string
  page_numbers: string[]
  citation_status?: string
}

type SummaryClauseOrRisk = {
  title: string
  details: string
  page_numbers: string[]
  citation_status?: string
}

type CitationValidation = {
  status: string
  checked_items: number
  evidence_matched_items: number
  invalid_references: unknown[]
  unverified_items: unknown[]
  method: string
}

type SummaryResponse = {
  document_id: string
  filename: string
  model: string
  executive_summary: string
  parties: SummaryParty[]
  key_dates: SummaryKeyDate[]
  payment_terms: SummaryPaymentTerm[]
  obligations: SummaryObligation[]
  important_clauses: SummaryClauseOrRisk[]
  potential_risks: SummaryClauseOrRisk[]
  disclaimer: string
  citation_validation: CitationValidation
}

type ExtractedPage = {
  page_number: number
  text: string
  character_count: number
  extraction_method: string
}

type ExtractionResponse = {
  filename: string
  page_count: number
  total_characters: number
  pages: ExtractedPage[]
}

type QuestionSource = {
  filename: string
  page_number: number | string
  passage: string
  similarity_score?: number
}

type QuestionResponse = {
  question: string
  answer: string
  sources: QuestionSource[]
  model?: string
}

type LayoutDetection = {
  page_number: number
  label: 'Table' | 'Figure'
  confidence: number
  bbox: number[]
  coordinate_space: string
  image_width: number
  image_height: number
}

type LayoutDetectionResponse = {
  filename: string
  page_count: number
  model: string
  confidence_threshold: number
  detection_count: number
  detections: LayoutDetection[]
  status: string
  saved_to: string
}

type TableExtractionItem = {
  page_number: number
  detection_confidence: number
  image_path: string
  text: string
  mean_word_confidence: number
  preprocessing: string
  ocr_engine: string
}

type TableExtractionResponse = {
  document_id: string
  table_count: number
  tables: TableExtractionItem[]
  saved_to: string
  status: string
}

type ChartBar = {
  bar_index: number
  estimated_value: number
  value_type: string
}

type ChartExtractionItem = {
  page_number: number
  detection_confidence: number
  image_path: string
  text: string
  mean_word_confidence: number
  ocr_engine: string
  preprocessing: string
  bar_analysis?: {
    status: string
    calibration: string
    axis_min: number
    axis_max: number
    bars: ChartBar[]
  }
}

type ChartExtractionResponse = {
  document_id: string
  chart_count: number
  charts: ChartExtractionItem[]
  saved_to: string
  status: string
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

function Icon({
  name,
  size = 20,
}: {
  name: IconName
  size?: number
}) {
  const paths: Record<IconName, ReactNode> = {
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
      </>
    ),
    files: (
      <>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <path d="M14 2v6h6M8 13h8M8 17h8" />
      </>
    ),
    search: (
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-4-4" />
      </>
    ),
    message: (
      <path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z" />
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.6a8 8 0 0 1-1.5.9l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.5-.9l-1.7.6-1.4-2.4L7.7 15a8 8 0 0 1 0-1.8l-1.4-1.1 1.4-2.4 1.7.6a8 8 0 0 1 1.5-.9l.3-1.8H14l.3 1.8a8 8 0 0 1 1.5.9l1.7-.6 1.4 2.4-1.4 1.1a8 8 0 0 1-.1 1.8z" />
      </>
    ),
    help: (
      <>
        <circle cx="12" cy="12" r="10" />
        <path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01" />
      </>
    ),
    upload: (
      <>
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <path d="m17 8-5-5-5 5M12 3v12" />
      </>
    ),
    shield: (
      <>
        <path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z" />
        <path d="m9 12 2 2 4-4" />
      </>
    ),
    clock: (
      <>
        <circle cx="12" cy="12" r="10" />
        <path d="M12 6v6l4 2" />
      </>
    ),
    arrow: <path d="M7 17 17 7M7 7h10v10" />,
    file: (
      <>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <path d="M14 2v6h6" />
      </>
    ),
    sparkles: (
      <>
        <path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-2-5.8L4 11l6-2.2L12 3z" />
        <path d="m19 14 1.2 2.8L23 18l-2.8 1.2L19 22l-1.2-2.8L15 18l2.8-1.2L19 14z" />
      </>
    ),
    menu: <path d="M4 6h16M4 12h16M4 18h16" />,
    check: <path d="m5 12 4 4L19 6" />,
    close: <path d="m18 6-12 12M6 6l12 12" />,
  }

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  )
}

const navigation: { label: string; icon: IconName }[] = [
  { label: 'Overview', icon: 'grid' },
  { label: 'My Documents', icon: 'files' },
  { label: 'Semantic Search', icon: 'search' },
  { label: 'AI Assistant', icon: 'message' },
]

function App() {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [activeNav, setActiveNav] = useState('Overview')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] =
    useState<UploadResponse | null>(null)
  const [uploadError, setUploadError] = useState('')
  
  const [isExtracting, setIsExtracting] = useState(false)
  const [extractionResult, setExtractionResult] =
    useState<ExtractionResponse | null>(null)
  const [extractionError, setExtractionError] = useState('')
  const [expandedPages, setExpandedPages] = useState<number[]>([1])

  const [isSummarizing, setIsSummarizing] = useState(false)
  const [summaryResult, setSummaryResult] = useState<SummaryResponse | null>(null)
  const [summaryError, setSummaryError] = useState('')

  const [isIndexing, setIsIndexing] = useState(false)
  const [isIndexed, setIsIndexed] = useState(false)
  const [indexError, setIndexError] = useState('')
  const [question, setQuestion] = useState('')
  const [isAsking, setIsAsking] = useState(false)
  const [questionResult, setQuestionResult] = useState<QuestionResponse | null>(null)
  const [questionError, setQuestionError] = useState('')

  const [isDetectingLayout, setIsDetectingLayout] = useState(false)
  const [layoutResult, setLayoutResult] =
    useState<LayoutDetectionResponse | null>(null)
  const [layoutError, setLayoutError] = useState('')

  const [isExtractingTables, setIsExtractingTables] = useState(false)
  const [tableResult, setTableResult] = useState<TableExtractionResponse | null>(null)
  const [tableError, setTableError] = useState('')
  const [isExtractingCharts, setIsExtractingCharts] = useState(false)
  const [chartResult, setChartResult] = useState<ChartExtractionResponse | null>(null)
  const [chartError, setChartError] = useState('')

  function handleFile(file?: File) {
    if (!file) return

    setUploadResult(null)
    setUploadError('')
    setExtractionResult(null)
    setExtractionError('')
    setSummaryResult(null)
    setSummaryError('')
    setIsIndexed(false)
    setIndexError('')
    setQuestionResult(null)
    setQuestionError('')
    setQuestion('')
    setLayoutResult(null)
    setLayoutError('')
    setTableResult(null)
    setTableError('')
    setChartResult(null)
    setChartError('')
    setExpandedPages([1])
    setFileError('')

    if (
      file.type !== 'application/pdf' &&
      !file.name.toLowerCase().endsWith('.pdf')
    ) {
      setFileError('Please select a PDF file.')
      setSelectedFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      return
    }

    if (file.size > 20 * 1024 * 1024) {
      setFileError('File size must be 20 MB or less.')
      setSelectedFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      return
    }

    setSelectedFile(file)
  }

  function resetFile() {
    setSelectedFile(null)
    setFileError('')
    setUploadError('')
    setUploadResult(null)
    setExtractionResult(null)
    setExtractionError('')
    setSummaryResult(null)
    setSummaryError('')
    setIsIndexed(false)
    setIndexError('')
    setQuestionResult(null)
    setQuestionError('')
    setQuestion('')
    setLayoutResult(null)
    setLayoutError('')

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  async function uploadDocument() {
    if (!selectedFile || isUploading || uploadResult) return

    setIsUploading(true)
    setUploadError('')
    setUploadResult(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(
        `${API_BASE_URL}/api/documents/upload`,
        {
          method: 'POST',
          body: formData,
        },
      )

      const data: unknown = await response.json()

      if (!response.ok) {
        let message = 'Document upload failed.'

        if (
          typeof data === 'object' &&
          data !== null &&
          'detail' in data &&
          typeof data.detail === 'string'
        ) {
          message = data.detail
        }

        throw new Error(message)
      }

      if (
        typeof data !== 'object' ||
        data === null ||
        !('document_id' in data) ||
        !('filename' in data) ||
        !('page_count' in data) ||
        !('size_bytes' in data) ||
        !('status' in data) ||
        !('message' in data)
      ) {
        throw new Error('The backend returned an unexpected response.')
      }

      setUploadResult(data as UploadResponse)
    } catch (error) {
      if (error instanceof TypeError) {
        setUploadError(
          'Cannot connect to the backend. Check that FastAPI is running and the API URL is correct.',
        )
      } else {
        setUploadError(
          error instanceof Error
            ? error.message
            : 'An unexpected error occurred during upload.',
        )
      }
    } finally {
      setIsUploading(false)
    }
  }


  async function extractDocumentText() {
    if (!uploadResult || isExtracting) return

    setIsExtracting(true)
    setExtractionError('')
    setExtractionResult(null)
    setExpandedPages([1])

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/documents/${encodeURIComponent(uploadResult.document_id)}/text`,
      )

      const data: unknown = await response.json()

      if (!response.ok) {
        const detail =
          typeof data === 'object' &&
          data !== null &&
          'detail' in data &&
          typeof data.detail === 'string'
            ? data.detail
            : 'Failed to extract PDF text.'

        throw new Error(detail)
      }

      if (
        typeof data !== 'object' ||
        data === null ||
        !('filename' in data) ||
        !('page_count' in data) ||
        !('total_characters' in data) ||
        !('pages' in data) ||
        !Array.isArray(data.pages)
      ) {
        throw new Error('The extraction API returned an unexpected response.')
      }

      setExtractionResult(data as ExtractionResponse)
      setActiveNav('My Documents')
    } catch (error) {
      setExtractionError(
        error instanceof TypeError
          ? 'Cannot connect to the backend. Check that FastAPI is running.'
          : error instanceof Error
            ? error.message
            : 'An unexpected extraction error occurred.',
      )
    } finally {
      setIsExtracting(false)
    }
  }


  async function summarizeDocument() {
    if (!uploadResult || isSummarizing || summaryResult) return

    setIsSummarizing(true)
    setSummaryError('')
    setSummaryResult(null)

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/documents/${encodeURIComponent(uploadResult.document_id)}/summarize`,
        { method: 'POST' },
      )

      const data: unknown = await response.json()

      if (!response.ok) {
        const detail =
          typeof data === 'object' &&
          data !== null &&
          'detail' in data &&
          typeof data.detail === 'string'
            ? data.detail
            : 'Document summarization failed.'
        throw new Error(detail)
      }

      if (
        typeof data !== 'object' ||
        data === null ||
        !('executive_summary' in data) ||
        !('parties' in data) ||
        !('key_dates' in data) ||
        !('payment_terms' in data) ||
        !('obligations' in data) ||
        !('important_clauses' in data) ||
        !('potential_risks' in data) ||
        !('disclaimer' in data)
      ) {
        throw new Error('The summarization API returned an unexpected response.')
      }

      setSummaryResult(data as SummaryResponse)
    } catch (error) {
      setSummaryError(
        error instanceof TypeError
          ? 'Cannot connect to the backend. Check that FastAPI is running.'
          : error instanceof Error
            ? error.message
            : 'An unexpected summarization error occurred.',
      )
    } finally {
      setIsSummarizing(false)
    }
  }

  async function indexDocument() {
    if (!uploadResult || isIndexing || isIndexed) return

    setIsIndexing(true)
    setIndexError('')
    setQuestionError('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/documents/${encodeURIComponent(uploadResult.document_id)}/index`,
        { method: 'POST' },
      )
      const data: unknown = await response.json().catch(() => ({}))

      if (!response.ok) {
        const detail =
          typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string'
            ? data.detail
            : 'Document indexing failed.'
        throw new Error(detail)
      }

      setIsIndexed(true)
      setActiveNav('AI Assistant')
    } catch (error) {
      setIndexError(
        error instanceof TypeError
          ? 'Cannot connect to the backend. Check that FastAPI is running.'
          : error instanceof Error
            ? error.message
            : 'An unexpected indexing error occurred.',
      )
    } finally {
      setIsIndexing(false)
    }
  }

  async function detectDocumentLayout() {
    if (!uploadResult || isDetectingLayout) return

    setIsDetectingLayout(true)
    setLayoutError('')
    setLayoutResult(null)

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/documents/${encodeURIComponent(uploadResult.document_id)}/layout-detection`,
        { method: 'POST' },
      )
      const data: unknown = await response.json().catch(() => ({}))

      if (!response.ok) {
        const detail =
          typeof data === 'object' &&
          data !== null &&
          'detail' in data &&
          typeof data.detail === 'string'
            ? data.detail
            : 'Document layout detection failed.'
        throw new Error(detail)
      }

      if (
        typeof data !== 'object' ||
        data === null ||
        !('filename' in data) ||
        !('page_count' in data) ||
        !('model' in data) ||
        !('confidence_threshold' in data) ||
        !('detection_count' in data) ||
        !('detections' in data) ||
        !Array.isArray(data.detections)
      ) {
        throw new Error('The layout-detection API returned an unexpected response.')
      }

      setLayoutResult(data as LayoutDetectionResponse)
    } catch (error) {
      setLayoutError(
        error instanceof TypeError
          ? 'Cannot connect to the backend. Check that FastAPI is running.'
          : error instanceof Error
            ? error.message
            : 'An unexpected layout-detection error occurred.',
      )
    } finally {
      setIsDetectingLayout(false)
    }
  }

  async function extractDocumentTables() {
    if (!uploadResult || isExtractingTables) return
    setIsExtractingTables(true)
    setTableError('')
    setTableResult(null)
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${encodeURIComponent(uploadResult.document_id)}/table-extraction`, { method: 'POST' })
      const data: unknown = await response.json().catch(() => ({}))
      if (!response.ok) {
        const detail = typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string' ? data.detail : 'Table extraction failed.'
        throw new Error(detail)
      }
      setTableResult(data as TableExtractionResponse)
    } catch (error) {
      setTableError(error instanceof TypeError ? 'Cannot connect to the backend. Check that FastAPI is running.' : error instanceof Error ? error.message : 'An unexpected table-extraction error occurred.')
    } finally {
      setIsExtractingTables(false)
    }
  }

  async function extractDocumentCharts() {
    if (!uploadResult || isExtractingCharts) return
    setIsExtractingCharts(true)
    setChartError('')
    setChartResult(null)
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/${encodeURIComponent(uploadResult.document_id)}/chart-extraction`, { method: 'POST' })
      const data: unknown = await response.json().catch(() => ({}))
      if (!response.ok) {
        const detail = typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string' ? data.detail : 'Chart extraction failed.'
        throw new Error(detail)
      }
      setChartResult(data as ChartExtractionResponse)
    } catch (error) {
      setChartError(error instanceof TypeError ? 'Cannot connect to the backend. Check that FastAPI is running.' : error instanceof Error ? error.message : 'An unexpected chart-extraction error occurred.')
    } finally {
      setIsExtractingCharts(false)
    }
  }

  async function askDocumentQuestion(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault()
    const trimmedQuestion = question.trim()

    if (!uploadResult || !isIndexed || !trimmedQuestion || isAsking) return

    setIsAsking(true)
    setQuestionError('')
    setQuestionResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/questions/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          question: trimmedQuestion,
          top_k: 3,
          document_id: uploadResult.document_id,
        }),
      })
      const data: unknown = await response.json().catch(() => ({}))

      if (!response.ok) {
        const detail =
          typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string'
            ? data.detail
            : 'Question answering failed.'
        throw new Error(detail)
      }

      if (
        typeof data !== 'object' || data === null ||
        !('answer' in data) || typeof data.answer !== 'string' ||
        !('sources' in data) || !Array.isArray(data.sources)
      ) {
        throw new Error('The question-answering API returned an unexpected response.')
      }

      setQuestionResult(data as QuestionResponse)
    } catch (error) {
      setQuestionError(
        error instanceof TypeError
          ? 'Cannot connect to the backend. Check that FastAPI is running.'
          : error instanceof Error
            ? error.message
            : 'An unexpected question-answering error occurred.',
      )
    } finally {
      setIsAsking(false)
    }
  }

  function renderPageReferences(pageNumbers: string[] | undefined) {
    if (!pageNumbers || pageNumbers.length === 0) {
      return <span className="citation-unverified">Source pages not verified</span>
    }

    return (
      <span className="summary-page-references">
        Pages: {pageNumbers.join(', ')}
      </span>
    )
  }

  function togglePage(pageNumber: number) {
    setExpandedPages((current) =>
      current.includes(pageNumber)
        ? current.filter((page) => page !== pageNumber)
        : [...current, pageNumber],
    )
  }

  return (
    <div className="app-shell">
      {mobileMenuOpen && (
        <button
          className="mobile-backdrop"
          aria-label="Close navigation"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <aside
        className={`sidebar ${mobileMenuOpen ? 'sidebar-open' : ''}`}
      >
        <a className="brand" href="#home" aria-label="LegalAI home">
          <span className="brand-mark">
            <Icon name="shield" size={23} />
          </span>
          <span className="brand-name">
            Legal<span>AI</span>
            <small>DOCUMENT INTELLIGENCE</small>
          </span>
        </a>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              key={item.label}
              className={`nav-item ${
                activeNav === item.label ? 'nav-active' : ''
              }`}
              onClick={() => {
                setActiveNav(item.label)
                setMobileMenuOpen(false)
              }}
            >
              <Icon name={item.icon} size={19} />
              <span>{item.label}</span>
              {item.label === 'My Documents' && (
                <span className="nav-count">
                  {uploadResult ? 1 : 0}
                </span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-divider" />

        <div className="workspace-label">PREFERENCES</div>

        <button
          className="nav-item"
          onClick={() => setActiveNav('Settings')}
        >
          <Icon name="settings" size={19} />
          <span>Settings</span>
        </button>

        <button
          className="nav-item"
          onClick={() => setActiveNav('Help & Support')}
        >
          <Icon name="help" size={19} />
          <span>Help &amp; Support</span>
        </button>

        <div className="sidebar-bottom">
          <div className="privacy-card">
            <span className="privacy-icon">
              <Icon name="shield" size={18} />
            </span>
            <strong>Your documents, protected.</strong>
            <p>
              AI-powered analysis with a focus on document privacy.
            </p>
          </div>

          <div className="profile-row">
            <div className="avatar">G</div>
            <div className="profile-copy">
              <strong>Guest workspace</strong>
              <span>Local session</span>
            </div>
            <span className="status-dot" />
          </div>
        </div>
      </aside>

      <main className="main-panel" id="home">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="mobile-menu-button"
              aria-label="Open navigation"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Icon name="menu" size={22} />
            </button>

            <div className="breadcrumb">
              Workspace <span>/</span> <strong>{activeNav}</strong>
            </div>
          </div>

          <div className="topbar-right">
            <span className="system-status">
              <span className="status-dot" /> AI workspace
            </span>
            <div className="topbar-avatar">G</div>
          </div>
        </header>

        <div className="dashboard-content">
          <section className="welcome-section">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-line" />
                YOUR LEGAL WORKSPACE
              </div>

              <h1>
                Understand every
                <br className="desktop-break" /> document{' '}
                <span>with clarity.</span>
              </h1>

              <p className="welcome-description">
                Upload a legal document. Extract key terms, uncover
                potential risks, and ask questions grounded in your source.
              </p>
            </div>

            <div className="welcome-art" aria-hidden="true">
              <div className="art-orbit orbit-one" />
              <div className="art-orbit orbit-two" />

              <div className="art-document">
                <div className="art-document-top">
                  <span />
                  <span />
                  <span />
                </div>
                <div className="art-shield">
                  <Icon name="shield" size={42} />
                </div>
                <div className="art-line art-line-long" />
                <div className="art-line" />
                <div className="art-line art-line-short" />
                <div className="art-highlight" />
              </div>

              <div className="art-chip">
                <Icon name="sparkles" size={15} /> AI analysis
              </div>

              <div className="art-check">
                <Icon name="check" size={17} />
              </div>
            </div>
          </section>

          <section className="upload-card">
            <div className="section-heading">
              <div>
                <span className="section-kicker">GET STARTED</span>
                <h2>Upload a document</h2>
                <p>
                  Start with a PDF and let LegalAI do the heavy reading.
                </p>
              </div>

              <span className="format-badge">
                <Icon name="file" size={15} /> PDF only
              </span>
            </div>

            <div
              className={`dropzone ${
                isDragging ? 'dropzone-active' : ''
              } ${selectedFile ? 'dropzone-selected' : ''}`}
              onDragOver={(event) => {
                event.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(event) => {
                event.preventDefault()
                setIsDragging(false)
                handleFile(event.dataTransfer.files[0])
              }}
            >
              <input
                ref={fileInputRef}
                className="visually-hidden"
                type="file"
                accept=".pdf,application/pdf"
                onChange={(event) =>
                  handleFile(event.target.files?.[0])
                }
                aria-label="Choose a PDF document"
              />

              <div className="upload-icon">
                <Icon
                  name={uploadResult ? 'check' : 'upload'}
                  size={24}
                />
              </div>

              {selectedFile ? (
                <>
                  <h3 className="selected-file-name">
                    {selectedFile.name}
                  </h3>
                  <p>
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    {' · '}
                    {uploadResult ? 'Uploaded successfully' : 'Ready for upload'}
                  </p>

                  {!isUploading && (
                    <button className="text-button" onClick={resetFile}>
                      Remove file
                    </button>
                  )}
                </>
              ) : (
                <>
                  <h3>
                    Drop your PDF here, or{' '}
                    <button
                      className="inline-link"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      browse files
                    </button>
                  </h3>
                  <p>PDF documents up to 20 MB</p>
                </>
              )}
            </div>

            {fileError && (
              <p className="error-message" role="alert">
                {fileError}
              </p>
            )}

            {uploadError && (
              <p className="error-message" role="alert">
                {uploadError}
              </p>
            )}

            <div className="upload-footer">
              <div className="upload-assurance">
                <Icon name="shield" size={16} />
                <span>Secure document processing</span>
              </div>

              <button
                className="primary-button"
                onClick={
                  selectedFile && !uploadResult
                    ? uploadDocument
                    : () => fileInputRef.current?.click()
                }
                disabled={isUploading || !!uploadResult}
              >
                {isUploading
                  ? 'Uploading...'
                  : uploadResult
                    ? 'Upload successful'
                    : selectedFile
                      ? 'Upload PDF'
                      : 'Select a document'}

                <Icon
                  name={uploadResult ? 'check' : 'arrow'}
                  size={17}
                />
              </button>
            </div>

            {uploadResult ? (
              <div className="upload-result" role="status">
                <div className="upload-result-heading">
                  <Icon name="check" size={18} />
                  <strong>Document uploaded successfully</strong>
                </div>

                <p>Filename: {uploadResult.filename}</p>
                <p>Pages: {uploadResult.page_count}</p>
                <p>
                  Size:{' '}
                  {(uploadResult.size_bytes / (1024 * 1024)).toFixed(2)} MB
                </p>
                <p>Document ID:</p>
                <code>{uploadResult.document_id}</code>

                <div className="document-actions">
                  <button
                    className="primary-button"
                    onClick={extractDocumentText}
                    disabled={isExtracting}
                  >
                    {isExtracting ? 'Extracting text...' : 'Extract PDF Text'}
                    <Icon name="file" size={17} />
                  </button>
                  <button
                    className="primary-button summary-button"
                    onClick={summarizeDocument}
                    disabled={isSummarizing || !!summaryResult}
                  >
                    {isSummarizing ? 'Generating summary...' : summaryResult ? 'Summary generated' : 'Generate Legal Summary'}
                    <Icon name={summaryResult ? 'check' : 'sparkles'} size={17} />
                  </button>
                  <button
                    className="primary-button index-button"
                    onClick={indexDocument}
                    disabled={isIndexing || isIndexed}
                  >
                    {isIndexing ? 'Indexing document...' : isIndexed ? 'Ready for Q&A' : 'Index for Q&A'}
                    <Icon name={isIndexed ? 'check' : 'search'} size={17} />
                  </button>
                  <button
                    className="primary-button"
                    onClick={detectDocumentLayout}
                    disabled={isDetectingLayout}
                  >
                    {isDetectingLayout ? 'Detecting layout...' : layoutResult ? 'Layout detected' : 'Detect Tables & Figures'}
                    <Icon name={layoutResult ? 'check' : 'search'} size={17} />
                  </button>
                  <button className="primary-button" onClick={extractDocumentTables} disabled={isExtractingTables}>
                    {isExtractingTables ? 'Extracting tables...' : tableResult ? 'Tables extracted' : 'Extract Tables (OCR)'}
                    <Icon name={tableResult ? 'check' : 'file'} size={17} />
                  </button>
                  <button className="primary-button" onClick={extractDocumentCharts} disabled={isExtractingCharts}>
                    {isExtractingCharts ? 'Extracting charts...' : chartResult ? 'Charts extracted' : 'Extract Charts (OCR)'}
                    <Icon name={chartResult ? 'check' : 'search'} size={17} />
                  </button>
                </div>
              </div>
            ) : (
              <p className="integration-note">
                {isUploading
                  ? 'Uploading and validating your PDF...'
                  : 'Your PDF will be validated by the LegalAI backend.'}
              </p>
            )}
          </section>


          {layoutError && (
            <div className="extraction-error" role="alert">
              <strong>Layout detection failed:</strong> {layoutError}
            </div>
          )}

          {layoutResult && (
            <section className="extraction-card">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">YOLO DOCUMENT ANALYSIS</span>
                  <h2>Layout detection results</h2>
                  <p>{layoutResult.filename}</p>
                </div>
                <span className="format-badge">{layoutResult.detection_count} detections</span>
              </div>

              <div className="extraction-stats">
                <div>
                  <strong>{layoutResult.detections.filter((item) => item.label === 'Table').length}</strong>
                  <span>Tables</span>
                </div>
                <div>
                  <strong>{layoutResult.detections.filter((item) => item.label === 'Figure').length}</strong>
                  <span>Figures</span>
                </div>
                <div>
                  <strong>{layoutResult.page_count}</strong>
                  <span>Pages scanned</span>
                </div>
              </div>

              {layoutResult.detections.length > 0 ? (
                <div className="summary-grid">
                  {layoutResult.detections.map((detection, index) => (
                    <article
                      className="summary-item"
                      key={`${detection.page_number}-${detection.label}-${index}`}
                    >
                      <strong>{detection.label} · Page {detection.page_number}</strong>
                      <p>
                        Confidence: {(detection.confidence * 100).toFixed(2)}%
                      </p>
                      <small>
                        Bounding box: {detection.bbox.map((value) => value.toFixed(1)).join(', ')}
                      </small>
                    </article>
                  ))}
                </div>
              ) : (
                <p className="summary-empty">
                  No tables or figures were detected in this document.
                </p>
              )}

              <p className="summary-disclaimer">
                Model: {layoutResult.model} · Confidence threshold: {layoutResult.confidence_threshold}
              </p>
            </section>
          )}

          {tableError && <div className="extraction-error" role="alert"><strong>Table extraction failed:</strong> {tableError}</div>}
          {tableResult && (
            <section className="extraction-card">
              <div className="section-heading"><div><span className="section-kicker">OCR TABLE EXTRACTION</span><h2>Extracted tables</h2><p>{tableResult.table_count} table(s) detected and processed</p></div><span className="format-badge">{tableResult.table_count} tables</span></div>
              {tableResult.tables.length ? <div className="summary-grid">{tableResult.tables.map((table, index) => <article className="summary-item" key={`${table.page_number}-${index}`}><strong>Table · Page {table.page_number}</strong><p>Detection confidence: {(table.detection_confidence * 100).toFixed(2)}% · OCR word confidence: {table.mean_word_confidence.toFixed(2)}%</p><pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{table.text || 'No text extracted.'}</pre></article>)}</div> : <p className="summary-empty">No table regions were extracted. Run layout detection first.</p>}
              <p className="summary-disclaimer">OCR confidence is a recognition score, not a guarantee of factual accuracy.</p>
            </section>
          )}

          {chartError && <div className="extraction-error" role="alert"><strong>Chart extraction failed:</strong> {chartError}</div>}
          {chartResult && (
            <section className="extraction-card">
              <div className="section-heading"><div><span className="section-kicker">OCR CHART EXTRACTION</span><h2>Extracted charts & figures</h2><p>{chartResult.chart_count} figure(s) processed</p></div><span className="format-badge">{chartResult.chart_count} figures</span></div>
              {chartResult.charts.length ? <div className="summary-grid">{chartResult.charts.map((chart, index) => <article className="summary-item" key={`${chart.page_number}-${index}`}><strong>Figure · Page {chart.page_number}</strong><p>Detection confidence: {(chart.detection_confidence * 100).toFixed(2)}% · OCR word confidence: {chart.mean_word_confidence.toFixed(2)}%</p><pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{chart.text || 'No text extracted.'}</pre>{chart.bar_analysis?.bars?.length ? <><strong>Approximate bar measurements</strong><ul>{chart.bar_analysis.bars.map((bar) => <li key={bar.bar_index}>Bar {bar.bar_index}: {bar.estimated_value.toFixed(1)}</li>)}</ul><small>Estimated values only; calibration: {chart.bar_analysis.calibration}.</small></> : null}</article>)}</div> : <p className="summary-empty">No figure regions were extracted. Run layout detection first.</p>}
              <p className="summary-disclaimer">Chart OCR may be imperfect. Bar measurements are approximate and only valid for the configured test-chart calibration.</p>
            </section>
          )}

          {extractionError && (
            <div className="extraction-error" role="alert">
              {extractionError}
            </div>
          )}

          {indexError && (
            <div className="extraction-error" role="alert">
              <strong>Indexing failed:</strong> {indexError}
            </div>
          )}

          {extractionResult && (
            <section className="extraction-card">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">DOCUMENT CONTENT</span>
                  <h2>Extracted text</h2>
                  <p>{extractionResult.filename}</p>
                </div>
                <span className="format-badge">
                  {extractionResult.page_count} pages
                </span>
              </div>

              <div className="extraction-stats">
                <div>
                  <strong>{extractionResult.page_count}</strong>
                  <span>Pages</span>
                </div>
                <div>
                  <strong>{extractionResult.total_characters.toLocaleString()}</strong>
                  <span>Characters</span>
                </div>
              </div>

              <div className="extracted-pages">
                {extractionResult.pages.map((page) => {
                  const isExpanded = expandedPages.includes(page.page_number)

                  return (
                    <article className="extracted-page" key={page.page_number}>
                      <button
                        className="page-toggle"
                        onClick={() => togglePage(page.page_number)}
                        aria-expanded={isExpanded}
                      >
                        <span>
                          <Icon name="file" size={17} />
                          Page {page.page_number}
                          <small>{page.character_count.toLocaleString()} characters</small>
                        </span>
                        <span>{isExpanded ? '−' : '+'}</span>
                      </button>

                      {isExpanded && (
                        <div className="page-content">
                          <div className="extraction-method">
                            Extraction method: {page.extraction_method}
                          </div>
                          <pre>{page.text}</pre>
                        </div>
                      )}
                    </article>
                  )
                })}
              </div>
            </section>
          )}


          {summaryError && (
            <div className="extraction-error" role="alert">
              <strong>Summarization failed:</strong> {summaryError}
            </div>
          )}

          {summaryResult && (
            <section className="summary-card">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">AI LEGAL ANALYSIS</span>
                  <h2>Document summary</h2>
                  <p>{summaryResult.filename}</p>
                </div>
                <span className={`citation-badge ${summaryResult.citation_validation?.status === 'passed' ? 'citation-passed' : 'citation-review'}`}>
                  Citation check: {summaryResult.citation_validation?.status ?? 'not available'}
                </span>
              </div>

              <div className="summary-executive">
                <h3><Icon name="sparkles" size={17} /> Executive summary</h3>
                <p>{summaryResult.executive_summary}</p>
              </div>

              <div className="summary-section">
                <h3>Parties</h3>
                {summaryResult.parties.length ? (
                  <div className="summary-grid">
                    {summaryResult.parties.map((party, index) => (
                      <article className="summary-item" key={`${party.name}-${index}`}>
                        <strong>{party.name}</strong>
                        <p>{party.role}</p>
                      </article>
                    ))}
                  </div>
                ) : <p className="summary-empty">No parties identified.</p>}
              </div>

              <div className="summary-section">
                <h3>Key dates</h3>
                {summaryResult.key_dates.length ? summaryResult.key_dates.map((item, index) => (
                  <article className="summary-item" key={`${item.event}-${index}`}>
                    <strong>{item.event}</strong>
                    <p>{item.date || 'Date not specified'}</p>
                    {renderPageReferences(item.page_numbers)}
                  </article>
                )) : <p className="summary-empty">No key dates identified.</p>}
              </div>

              <div className="summary-section">
                <h3>Payment terms</h3>
                {summaryResult.payment_terms.length ? summaryResult.payment_terms.map((item, index) => (
                  <article className="summary-item" key={`${item.term}-${index}`}>
                    <strong>{item.term}</strong>
                    <p>{item.details}</p>
                    {renderPageReferences(item.page_numbers)}
                  </article>
                )) : <p className="summary-empty">No payment terms identified.</p>}
              </div>

              <div className="summary-section">
                <h3>Obligations</h3>
                {summaryResult.obligations.length ? summaryResult.obligations.map((item, index) => (
                  <article className="summary-item" key={`${item.party}-${index}`}>
                    <strong>{item.party}</strong>
                    <p>{item.obligation}</p>
                    {renderPageReferences(item.page_numbers)}
                  </article>
                )) : <p className="summary-empty">No obligations identified.</p>}
              </div>

              <div className="summary-section">
                <h3>Important clauses</h3>
                {summaryResult.important_clauses.length ? summaryResult.important_clauses.map((item, index) => (
                  <article className="summary-item" key={`${item.title}-${index}`}>
                    <strong>{item.title}</strong>
                    <p>{item.details}</p>
                    {renderPageReferences(item.page_numbers)}
                  </article>
                )) : <p className="summary-empty">No important clauses identified.</p>}
              </div>

              <div className="summary-section">
                <h3>Potential risks to review</h3>
                {summaryResult.potential_risks.length ? summaryResult.potential_risks.map((item, index) => (
                  <article className="summary-item summary-risk" key={`${item.title}-${index}`}>
                    <strong>{item.title}</strong>
                    <p>{item.details}</p>
                    {renderPageReferences(item.page_numbers)}
                  </article>
                )) : <p className="summary-empty">No potential risks identified by the model.</p>}
              </div>

              {summaryResult.citation_validation && (
                <div className="citation-validation">
                  <strong>Citation validation</strong>
                  <p>
                    {summaryResult.citation_validation.evidence_matched_items} of{' '}
                    {summaryResult.citation_validation.checked_items} items had matching textual evidence.
                  </p>
                  <small>{summaryResult.citation_validation.method}</small>
                  {summaryResult.citation_validation.unverified_items.length > 0 && (
                    <p className="citation-unverified">
                      Some citations could not be verified. Review these items against the original PDF.
                    </p>
                  )}
                </div>
              )}

              <p className="summary-disclaimer">{summaryResult.disclaimer}</p>
            </section>
          )}

          <section className="qa-card" id="ask-your-document">
            <div className="section-heading">
              <div>
                <span className="section-kicker">DOCUMENT-GROUNDED Q&A</span>
                <h2>Ask your document</h2>
                <p>Ask a question and review the passages retrieved from your PDF.</p>
              </div>
              <span className={`format-badge ${isIndexed ? 'qa-ready-badge' : ''}`}>
                {isIndexed ? 'Document indexed' : 'Index required'}
              </span>
            </div>

            {!uploadResult ? (
              <div className="qa-empty-state">
                <Icon name="files" size={24} />
                <strong>Upload a PDF to get started</strong>
                <p>After uploading, index the document to enable source-grounded questions.</p>
              </div>
            ) : !isIndexed ? (
              <div className="qa-empty-state">
                <Icon name="search" size={24} />
                <strong>Your document needs indexing</strong>
                <p>Use the “Index for Q&amp;A” button in the upload result before asking questions.</p>
                <button className="primary-button" onClick={indexDocument} disabled={isIndexing}>
                  {isIndexing ? 'Indexing document...' : 'Index document now'}
                  <Icon name="arrow" size={17} />
                </button>
              </div>
            ) : (
              <>
                <form className="qa-form" onSubmit={askDocumentQuestion}>
                  <label htmlFor="legalai-question">Your question</label>
                  <textarea
                    id="legalai-question"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="e.g. When must the client pay an invoice?"
                    rows={3}
                    maxLength={2000}
                    required
                    disabled={isAsking}
                  />
                  <div className="qa-form-footer">
                    <span>{question.length}/2000 characters · Answers use the selected document only.</span>
                    <button className="primary-button" type="submit" disabled={isAsking || question.trim().length < 3}>
                      {isAsking ? 'Finding answer...' : 'Ask question'}
                      <Icon name="arrow" size={17} />
                    </button>
                  </div>
                </form>

                {questionError && (
                  <div className="extraction-error" role="alert">
                    <strong>Question failed:</strong> {questionError}
                  </div>
                )}

                {questionResult && (
                  <div className="qa-answer" aria-live="polite">
                    <div className="qa-answer-heading">
                      <span className="qa-answer-icon"><Icon name="sparkles" size={17} /></span>
                      <div>
                        <span className="section-kicker">LEGALAI RESPONSE</span>
                        <h3>{questionResult.question}</h3>
                      </div>
                    </div>
                    <p className="qa-answer-text">{questionResult.answer}</p>

                    <div className="qa-sources">
                      <h4>Retrieved source passages ({questionResult.sources.length})</h4>
                      {questionResult.sources.length ? questionResult.sources.map((source, index) => (
                        <article className="qa-source" key={`${source.filename}-${source.page_number}-${index}`}>
                          <div className="qa-source-meta">
                            <strong>{source.filename}</strong>
                            <span>Page {source.page_number}</span>
                          </div>
                          <p>{source.passage}</p>
                          {typeof source.similarity_score === 'number' && (
                            <small>Retrieval similarity: {(source.similarity_score * 100).toFixed(1)}%</small>
                          )}
                        </article>
                      )) : (
                        <p className="summary-empty">No supporting passages were returned. Treat the answer as unsupported.</p>
                      )}
                    </div>
                    <p className="summary-disclaimer">AI-generated information, not legal advice. Always check the cited passage in the original document.</p>
                  </div>
                )}
              </>
            )}
          </section>

          <section className="workflow-section">
            <div className="section-heading workflow-heading">
              <div>
                <span className="section-kicker">YOUR WORKFLOW</span>
                <h2>From document to insight</h2>
              </div>
              <span className="muted-label">Three simple steps</span>
            </div>

            <div className="workflow-grid">
              <article className="workflow-card">
                <div className="workflow-icon workflow-blue">
                  <Icon name="files" size={21} />
                </div>
                <span className="step-number">01 / INGEST</span>
                <h3>Upload &amp; extract</h3>
                <p>
                  Extract readable text from PDFs, with OCR fallback for
                  scanned pages.
                </p>
                <span className="workflow-status">
                  <span className="status-dot status-grey" /> Ready to connect
                </span>
              </article>

              <article className="workflow-card">
                <div className="workflow-icon workflow-violet">
                  <Icon name="sparkles" size={21} />
                </div>
                <span className="step-number">02 / ANALYZE</span>
                <h3>Summarize &amp; review</h3>
                <p>
                  Surface parties, payment terms, obligations, key clauses,
                  and review points.
                </p>
                <span className="workflow-status">
                  <span className="status-dot status-grey" /> Ready to connect
                </span>
              </article>

              <article className="workflow-card">
                <div className="workflow-icon workflow-green">
                  <Icon name="search" size={21} />
                </div>
                <span className="step-number">03 / EXPLORE</span>
                <h3>Ask your document</h3>
                <p>
                  Search for relevant passages and ask questions with
                  page-level references.
                </p>
                <span className="workflow-status">
                  <span className="status-dot status-grey" /> Ready to connect
                </span>
              </article>
            </div>
          </section>

          <section className="empty-documents">
            <div className="empty-doc-icon">
              <Icon name="files" size={21} />
            </div>

            <div>
              <h3>Your document library</h3>
              <p>
                {uploadResult
                  ? `${uploadResult.filename} is uploaded in this session.`
                  : 'Uploaded documents will appear here once backend integration is connected.'}
              </p>
            </div>

            <span className="library-count">
              {uploadResult ? '1 document' : '0 documents'}
            </span>
          </section>

          <footer className="dashboard-footer">
            <span>
              LegalAI <span className="footer-dot">·</span> Document
              intelligence workspace
            </span>

            <span>
              <Icon name="shield" size={14} /> AI-generated analysis is not
              legal advice.
            </span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App
