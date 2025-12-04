from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID


class SearchQuery(BaseModel):
    """Schema de request para busca full-text"""
    query: str = Field(..., min_length=1, max_length=500, description="Texto da busca")
    workspace_id: UUID = Field(..., description="ID do workspace para buscar")
    type_filter: Optional[Literal[
        "pages_only",
        "paragraph",
        "heading1",
        "heading2",
        "heading3",
        "code",
        "quote",
        "bullet_list",
        "numbered_list",
        "image"
    ]] = Field(None, description="Filtrar por tipo de conteúdo")
    include_archived: bool = Field(default=False, description="Incluir páginas arquivadas")
    limit: int = Field(default=20, ge=1, le=100, description="Máximo de resultados")
    offset: int = Field(default=0, ge=0, description="Offset para paginação")


class SearchResultBlock(BaseModel):
    """Resultado de busca em bloco"""
    block_id: UUID
    page_id: UUID
    block_type: str
    content_text: str
    highlight: str  # HTML com tags <mark>
    rank: float

    model_config = ConfigDict(from_attributes=True)


class SearchResultPage(BaseModel):
    """Resultado de busca em página"""
    page_id: UUID
    page_title: str
    page_icon: Optional[str] = None
    workspace_id: UUID
    is_archived: bool
    highlight: str  # Título ou snippet destacado com <mark>
    rank: float
    matched_in: Literal["title", "content"]  # Onde foi encontrado
    created_at: datetime
    updated_at: datetime

    # Blocos correspondentes (se houver)
    matched_blocks: List[SearchResultBlock] = []

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    """Resposta da busca com resultados e metadados"""
    results: List[SearchResultPage]
    total: int  # Total de resultados (para paginação)
    query: str
    execution_time_ms: float  # Métrica de performance
