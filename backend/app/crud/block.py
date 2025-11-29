from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.block import Block
from app.schemas.block import BlockCreate, BlockUpdate, BlockMove


def create(db: Session, block_in: BlockCreate) -> Block:
    """Create a new block"""
    block = Block(
        page_id=block_in.page_id,
        parent_block_id=block_in.parent_block_id,
        type=block_in.type,
        content=block_in.content,
        order=block_in.order
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def get_by_id(db: Session, block_id: UUID) -> Optional[Block]:
    """Get block by ID"""
    return db.query(Block).filter(Block.id == block_id).first()


def get_by_page(db: Session, page_id: UUID) -> List[Block]:
    """Get all blocks in a page, ordered"""
    return db.query(Block).filter(
        Block.page_id == page_id
    ).order_by(Block.order).all()


def update(db: Session, block: Block, block_in: BlockUpdate) -> Block:
    """Update block"""
    update_data = block_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(block, field, value)
    db.commit()
    db.refresh(block)
    return block


def move(db: Session, block: Block, move_data: BlockMove) -> Block:
    """Reorder block and/or change parent"""
    block.order = move_data.new_order
    if move_data.new_parent_block_id is not None:
        block.parent_block_id = move_data.new_parent_block_id
    db.commit()
    db.refresh(block)
    return block


def delete(db: Session, block: Block) -> None:
    """Delete block"""
    db.delete(block)
    db.commit()
