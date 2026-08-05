"""Response shapes for the API.

Every endpoint declares a `response_model`. That buys three things at once: FastAPI validates
what we return, the auto-generated docs at http://localhost:8000/docs stay accurate, and the
web app's TypeScript types in `web/src/lib/types.ts` have something to mirror.

When you add an endpoint, add its model here first - it's the contract, and it's the quickest
way to agree on a shape before anyone writes the query or the chart.
"""


from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str
    database: str = Field(description="Which backend is serving: 'postgres' or 'sqlite'")
    version: str


class Utilization(BaseModel):
    total_consultants: int
    consultants_on_bench: int
    billable_hours: int
    bench_hours: int
    utilization_pct: float = Field(description="billable / (billable + bench), as a percentage")


class BenchBySeniorityRow(BaseModel):
    seniority: str
    on_bench: int


class BenchBySeniority(BaseModel):
    rows: list[BenchBySeniorityRow]


class TrendPoint(BaseModel):
    week_ending: str
    billable_hours: int
    bench_hours: int
    utilization_pct: float


class UtilizationTrend(BaseModel):
    rows: list[TrendPoint]


class FunnelStage(BaseModel):
    stage: str
    count: int
    pct_of_total: float


class Funnel(BaseModel):
    rows: list[FunnelStage]
    total: int


class ConsultantSummary(BaseModel):
    consultant_id: int
    name: str
    skills: str
    seniority: str
    location: str
    status: str
    days_on_bench: int | None = None


class ConsultantPage(BaseModel):
    """One page of consultants, plus enough metadata to render pagination controls."""

    rows: list[ConsultantSummary]
    total: int = Field(description="Total matching consultants, ignoring pagination")
    page: int
    page_size: int
    pages: int


class RiskFactor(BaseModel):
    label: str
    contribution: float


class RiskScore(BaseModel):
    consultant_id: int
    risk_score: float = Field(ge=0, le=1, description="0 = low risk, 1 = high risk")
    band: str = Field(description="low / medium / high")
    factors: list[RiskFactor]
    model: str = Field(description="Which scorer produced this - swap when the ML model lands")


class ConsultantDetail(BaseModel):
    consultant_id: int
    name: str
    skills: str
    seniority: str
    location: str
    status: str
    cost_rate: int
    hire_date: str
    days_on_bench: int | None = None
    risk: RiskScore
