from sqlalchemy.orm import Session
from sqlalchemy import func, literal_column, and_
from typing import List, Tuple
from uuid import UUID
import time

from app.models.page import Page
from app.models.block import Block
from app.schemas.search import SearchQuery, SearchResultPage, SearchResultBlock


def _is_postgresql(db: Session) -> bool:
    """Verifica se o banco é PostgreSQL"""
    return db.bind.dialect.name == 'postgresql'


def search_workspace(
    db: Session,
    search_query: SearchQuery
) -> Tuple[List[SearchResultPage], int, float]:
    """
    Busca full-text em páginas e blocos de um workspace.

    Args:
        db: Sessão do banco de dados
        search_query: Parâmetros da busca

    Returns:
        Tupla com (resultados, total, tempo_execucao_ms)
    """
    start_time = time.time()

    # Fallback para não-PostgreSQL (desenvolvimento)
    if not _is_postgresql(db):
        return _fallback_search(db, search_query, start_time)

    # Construir query PostgreSQL full-text search
    # plainto_tsquery converte texto simples em tsquery (trata stemming)
    ts_query = func.plainto_tsquery('portuguese', search_query.query)

    # === BUSCA EM PÁGINAS ===
    # Busca em títulos de páginas usando title_search tsvector
    pages_query = db.query(
        Page.id.label('page_id'),
        Page.title.label('page_title'),
        Page.icon.label('page_icon'),
        Page.workspace_id,
        Page.is_archived,
        Page.created_at,
        Page.updated_at,
        # ts_rank calcula relevância (0.0 a 1.0)
        func.ts_rank(
            literal_column('pages.title_search'),
            ts_query
        ).label('rank'),
        # ts_headline gera snippet com <mark> tags
        func.ts_headline(
            'portuguese',
            Page.title,
            ts_query,
            'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=25'
        ).label('highlight'),
        literal_column("'title'").label('matched_in'),
        literal_column('NULL::uuid').label('block_id'),
        literal_column('NULL::varchar').label('block_type')
    ).filter(
        Page.workspace_id == search_query.workspace_id,
        literal_column('pages.title_search').op('@@')(ts_query)
    )

    # Filtro de arquivados
    if not search_query.include_archived:
        pages_query = pages_query.filter(Page.is_archived == False)

    # === BUSCA EM BLOCOS ===
    blocks_query = None

    # Se type_filter é "pages_only", não buscar em blocos
    if search_query.type_filter != "pages_only":
        blocks_query = db.query(
            Page.id.label('page_id'),
            Page.title.label('page_title'),
            Page.icon.label('page_icon'),
            Page.workspace_id,
            Page.is_archived,
            Page.created_at,
            Page.updated_at,
            # Rank dos blocos (peso B, menor que títulos)
            func.ts_rank(
                literal_column('blocks.content_search'),
                ts_query
            ).label('rank'),
            # Headline do conteúdo do bloco
            func.ts_headline(
                'portuguese',
                func.coalesce(literal_column("blocks.content->>'text'"), ''),
                ts_query,
                'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=25'
            ).label('highlight'),
            literal_column("'content'").label('matched_in'),
            Block.id.label('block_id'),
            Block.type.label('block_type')
        ).join(
            Page, Block.page_id == Page.id
        ).filter(
            Page.workspace_id == search_query.workspace_id,
            literal_column('blocks.content_search').op('@@')(ts_query)
        )

        # Filtro de arquivados
        if not search_query.include_archived:
            blocks_query = blocks_query.filter(Page.is_archived == False)

        # Filtro de tipo de bloco
        if search_query.type_filter:
            blocks_query = blocks_query.filter(Block.type == search_query.type_filter)

    # === COMBINAR RESULTADOS ===
    if blocks_query is not None:
        # União de páginas e blocos
        combined_query = pages_query.union_all(blocks_query)
    else:
        combined_query = pages_query

    # Ordenar por relevância (maior rank primeiro)
    combined_query = combined_query.order_by(literal_column('rank').desc())

    # Obter total (antes da paginação)
    # Usar subquery para contar
    from sqlalchemy import select
    total_query = select(func.count()).select_from(combined_query.subquery())
    total = db.execute(total_query).scalar()

    # Aplicar paginação
    combined_query = combined_query.limit(search_query.limit).offset(search_query.offset)

    # Executar query
    raw_results = combined_query.all()

    # === PÓS-PROCESSAMENTO ===
    # Agrupar blocos por página para apresentar melhor os resultados
    pages_dict = {}

    for row in raw_results:
        page_id = str(row.page_id)

        if page_id not in pages_dict:
            # Nova página nos resultados
            pages_dict[page_id] = SearchResultPage(
                page_id=row.page_id,
                page_title=row.page_title,
                page_icon=row.page_icon,
                workspace_id=row.workspace_id,
                is_archived=row.is_archived,
                highlight=row.highlight,
                rank=row.rank,
                matched_in=row.matched_in,
                created_at=row.created_at,
                updated_at=row.updated_at,
                matched_blocks=[]
            )
        else:
            # Página já existe, adicionar bloco aos matched_blocks
            if row.matched_in == 'content' and row.block_id:
                pages_dict[page_id].matched_blocks.append(
                    SearchResultBlock(
                        block_id=row.block_id,
                        page_id=row.page_id,
                        block_type=row.block_type,
                        content_text=row.highlight,  # Já vem com highlight
                        highlight=row.highlight,
                        rank=row.rank
                    )
                )
                # Atualizar rank da página se o bloco tiver rank maior
                if row.rank > pages_dict[page_id].rank:
                    pages_dict[page_id].rank = row.rank

    # Converter para lista e ordenar por rank
    results = sorted(
        pages_dict.values(),
        key=lambda x: x.rank,
        reverse=True
    )

    # Limitar ao número solicitado (após agrupamento)
    results = results[:search_query.limit]

    execution_time = (time.time() - start_time) * 1000  # Converter para ms

    return results, total, execution_time


def _fallback_search(
    db: Session,
    search_query: SearchQuery,
    start_time: float
) -> Tuple[List[SearchResultPage], int, float]:
    """
    Busca fallback para SQLite usando LIKE.
    Implementação simples para ambiente de desenvolvimento.
    """
    results = []

    # Busca simples com LIKE nos títulos das páginas
    pages = db.query(Page).filter(
        Page.workspace_id == search_query.workspace_id,
        Page.title.ilike(f'%{search_query.query}%')
    )

    if not search_query.include_archived:
        pages = pages.filter(Page.is_archived == False)

    # Aplicar paginação
    total = pages.count()
    pages = pages.limit(search_query.limit).offset(search_query.offset).all()

    for page in pages:
        results.append(
            SearchResultPage(
                page_id=page.id,
                page_title=page.title,
                page_icon=page.icon,
                workspace_id=page.workspace_id,
                is_archived=page.is_archived,
                highlight=page.title,  # Sem highlight no SQLite
                rank=0.0,
                matched_in='title',
                created_at=page.created_at,
                updated_at=page.updated_at,
                matched_blocks=[]
            )
        )

    execution_time = (time.time() - start_time) * 1000
    return results, total, execution_time
