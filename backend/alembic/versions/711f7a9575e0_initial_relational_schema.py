"""initial_relational_schema

Revision ID: 711f7a9575e0
Revises: 
Create Date: 2026-10-09 15:10:52.750457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '711f7a9575e0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Canonical PostgreSQL ENUM type objects
user_role_enum = postgresql.ENUM('FARMER', 'FPO_REPRESENTATIVE', 'BUYER', 'ADMIN', name='user_role')
farmer_kyc_status_enum = postgresql.ENUM('PENDING', 'VERIFIED', 'REJECTED', name='farmer_kyc_status')
buyer_verification_status_enum = postgresql.ENUM('PENDING', 'VERIFIED', 'REJECTED', name='buyer_verification_status')
fpo_membership_status_enum = postgresql.ENUM('PENDING', 'ACTIVE', 'REJECTED', name='fpo_membership_status')
buyer_category_enum = postgresql.ENUM('INSTITUTIONAL_PROCESSOR', 'WHOLESALER', 'COMMISSION_AGENT', 'RETAILER_EXPORTER', name='buyer_category')
verification_doc_type_enum = postgresql.ENUM('GSTIN', 'APMC_LICENSE', 'FSSAI_REGISTRATION', 'TRADE_LICENSE', 'PAN', name='verification_doc_type')
crop_category_enum = postgresql.ENUM('CEREALS', 'PULSES', 'OILSEEDS', 'VEGETABLES', 'FRUITS', name='crop_category')
standard_unit_enum = postgresql.ENUM('QUINTAL', 'KG', name='standard_unit')
quality_grade_enum = postgresql.ENUM('GRADE_A', 'GRADE_B', 'GRADE_C', name='quality_grade')
lot_status_enum = postgresql.ENUM('DRAFT', 'AVAILABLE', 'AGGREGATED', 'COMMITTED', 'SOLD', 'CANCELLED', name='lot_status')
sale_intent_status_enum = postgresql.ENUM('ACTIVE', 'SUSPENDED_POOLED', 'MATCHED', 'CLOSED', 'CANCELLED', name='sale_intent_status')
data_source_tier_enum = postgresql.ENUM('DISTRICT', 'STATE', 'NATIONAL_BASELINE', name='data_source_tier')
buyer_demand_status_enum = postgresql.ENUM('OPEN', 'FULFILLED', 'CANCELLED', name='buyer_demand_status')
offer_status_enum = postgresql.ENUM('PENDING', 'COUNTERED', 'ACCEPTED', 'REJECTED', 'EXPIRED', name='offer_status')
order_status_enum = postgresql.ENUM('CONFIRMED', 'DISPATCHED', 'DELIVERED', 'COMPLETED', 'CANCELLED', name='order_status')
allocation_payout_status_enum = postgresql.ENUM('PENDING', 'DISBURSED', 'CONFIRMED_BY_FARMER', name='allocation_payout_status')
logistics_status_enum = postgresql.ENUM('PENDING_PICKUP', 'IN_TRANSIT', 'DELIVERED', name='logistics_status')
payment_stage_enum = postgresql.ENUM('ADVANCE', 'FINAL_SETTLEMENT', name='payment_stage')
payment_method_enum = postgresql.ENUM('BANK_TRANSFER', 'UPI', 'OFFLINE_CASH', 'FUTURE_RAZORPAY', name='payment_method')
payment_status_enum = postgresql.ENUM('SUBMITTED', 'VERIFIED_BY_SELLER', 'DISPUTED', name='payment_status')
grievance_category_enum = postgresql.ENUM('QUALITY_DEFECT', 'WEIGHT_SHORTAGE', 'PAYMENT_DELAY', 'TRANSIT_DAMAGE', name='grievance_category')
grievance_status_enum = postgresql.ENUM('OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED', name='grievance_status')

def upgrade() -> None:
    # 1. Create all 22 canonical PostgreSQL ENUM types
    user_role_enum.create(op.get_bind(), checkfirst=True)
    farmer_kyc_status_enum.create(op.get_bind(), checkfirst=True)
    buyer_verification_status_enum.create(op.get_bind(), checkfirst=True)
    fpo_membership_status_enum.create(op.get_bind(), checkfirst=True)
    buyer_category_enum.create(op.get_bind(), checkfirst=True)
    verification_doc_type_enum.create(op.get_bind(), checkfirst=True)
    crop_category_enum.create(op.get_bind(), checkfirst=True)
    standard_unit_enum.create(op.get_bind(), checkfirst=True)
    quality_grade_enum.create(op.get_bind(), checkfirst=True)
    lot_status_enum.create(op.get_bind(), checkfirst=True)
    sale_intent_status_enum.create(op.get_bind(), checkfirst=True)
    data_source_tier_enum.create(op.get_bind(), checkfirst=True)
    buyer_demand_status_enum.create(op.get_bind(), checkfirst=True)
    offer_status_enum.create(op.get_bind(), checkfirst=True)
    order_status_enum.create(op.get_bind(), checkfirst=True)
    allocation_payout_status_enum.create(op.get_bind(), checkfirst=True)
    logistics_status_enum.create(op.get_bind(), checkfirst=True)
    payment_stage_enum.create(op.get_bind(), checkfirst=True)
    payment_method_enum.create(op.get_bind(), checkfirst=True)
    payment_status_enum.create(op.get_bind(), checkfirst=True)
    grievance_category_enum.create(op.get_bind(), checkfirst=True)
    grievance_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create tables in dependency order
    op.create_table(
        'crops',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', postgresql.ENUM('CEREALS', 'PULSES', 'OILSEEDS', 'VEGETABLES', 'FRUITS', name='crop_category', create_type=False), nullable=False),
        sa.Column('standard_unit', postgresql.ENUM('QUINTAL', 'KG', name='standard_unit', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_crops_name', 'crops', ['name'], unique=True)
    op.create_table(
        'pincode_coordinates',
        sa.Column('pincode', sa.String(length=6), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('pincode'),
    )
    op.create_index('ix_pincode_coordinates_district', 'pincode_coordinates', ['district'], unique=False)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', postgresql.ENUM('FARMER', 'FPO_REPRESENTATIVE', 'BUYER', 'ADMIN', name='user_role', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_phone_number', 'users', ['phone_number'], unique=True)
    op.create_table(
        'buyer_demands',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('buyer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crop_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('required_quantity', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('acceptable_grades', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('max_budget_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('delivery_destination_pincode', sa.String(length=6), nullable=False),
        sa.Column('required_by_date', sa.Date(), nullable=False),
        sa.Column('status', postgresql.ENUM('OPEN', 'FULFILLED', 'CANCELLED', name='buyer_demand_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('max_budget_price > 0', name='chk_buyer_demand_budget_positive'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('required_quantity > 0', name='chk_buyer_demand_quantity_positive'),
    )
    op.create_index('ix_buyer_demands_buyer_id', 'buyer_demands', ['buyer_id'], unique=False)
    op.create_index('ix_buyer_demands_delivery_destination_pincode', 'buyer_demands', ['delivery_destination_pincode'], unique=False)
    op.create_index('ix_buyer_demands_crop_id', 'buyer_demands', ['crop_id'], unique=False)
    op.create_table(
        'buyer_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('buyer_category', postgresql.ENUM('INSTITUTIONAL_PROCESSOR', 'WHOLESALER', 'COMMISSION_AGENT', 'RETAILER_EXPORTER', name='buyer_category', create_type=False), nullable=False),
        sa.Column('gstin', sa.String(length=15), nullable=True),
        sa.Column('verification_doc_type', postgresql.ENUM('GSTIN', 'APMC_LICENSE', 'FSSAI_REGISTRATION', 'TRADE_LICENSE', 'PAN', name='verification_doc_type', create_type=False), nullable=False),
        sa.Column('verification_doc_number', sa.String(length=50), nullable=False),
        sa.Column('verification_status', postgresql.ENUM('PENDING', 'VERIFIED', 'REJECTED', name='buyer_verification_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_buyer_profiles_user_id', 'buyer_profiles', ['user_id'], unique=True)
    op.create_table(
        'farmer_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('pincode', sa.String(length=6), nullable=False),
        sa.Column('land_holding_acres', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('kyc_status', postgresql.ENUM('PENDING', 'VERIFIED', 'REJECTED', name='farmer_kyc_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_farmer_profiles_district', 'farmer_profiles', ['district'], unique=False)
    op.create_index('ix_farmer_profiles_pincode', 'farmer_profiles', ['pincode'], unique=False)
    op.create_index('ix_farmer_profiles_user_id', 'farmer_profiles', ['user_id'], unique=True)
    op.create_table(
        'fpos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('registration_number', sa.String(length=100), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fpos_district', 'fpos', ['district'], unique=False)
    op.create_index('ix_fpos_registration_number', 'fpos', ['registration_number'], unique=True)
    op.create_table(
        'market_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crop_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mandi_name', sa.String(length=150), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('min_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('max_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('modal_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('price_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('min_price <= modal_price AND modal_price <= max_price', name='chk_market_price_spread'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('min_price > 0', name='chk_market_price_positive'),
    )
    op.create_index('ix_market_prices_district', 'market_prices', ['district'], unique=False)
    op.create_index('ix_market_prices_price_date', 'market_prices', ['price_date'], unique=False)
    op.create_index('ix_market_prices_crop_id', 'market_prices', ['crop_id'], unique=False)
    op.create_index('ix_market_prices_state', 'market_prices', ['state'], unique=False)
    op.create_index('ix_market_prices_crop_district_date', 'market_prices', ['crop_id', 'district', 'price_date'], unique=False)
    op.create_table(
        'fpo_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fpo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'ACTIVE', 'REJECTED', name='fpo_membership_status', create_type=False), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['fpo_id'], ['fpos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['farmer_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('fpo_id', 'farmer_user_id', name='uq_fpo_membership_farmer'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fpo_memberships_farmer_user_id', 'fpo_memberships', ['farmer_user_id'], unique=False)
    op.create_index('ix_fpo_memberships_fpo_id', 'fpo_memberships', ['fpo_id'], unique=False)
    op.create_table(
        'lots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fpo_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('crop_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('quality_grade', postgresql.ENUM('GRADE_A', 'GRADE_B', 'GRADE_C', name='quality_grade', create_type=False), nullable=False),
        sa.Column('moisture_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('storage_location_pincode', sa.String(length=6), nullable=False),
        sa.Column('is_aggregated', sa.Boolean(), nullable=False),
        sa.Column('parent_fpo_lot_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', postgresql.ENUM('DRAFT', 'AVAILABLE', 'AGGREGATED', 'COMMITTED', 'SOLD', 'CANCELLED', name='lot_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['farmer_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['parent_fpo_lot_id'], ['lots.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['fpo_id'], ['fpos.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('((farmer_user_id IS NOT NULL AND fpo_id IS NULL) OR (farmer_user_id IS NULL AND fpo_id IS NOT NULL))', name='chk_lot_ownership'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('quantity > 0', name='chk_lot_quantity_positive'),
    )
    op.create_index('ix_lots_fpo_id', 'lots', ['fpo_id'], unique=False)
    op.create_index('ix_lots_storage_location_pincode', 'lots', ['storage_location_pincode'], unique=False)
    op.create_index('ix_lots_farmer_user_id', 'lots', ['farmer_user_id'], unique=False)
    op.create_index('ix_lots_crop_id', 'lots', ['crop_id'], unique=False)
    op.create_index('ix_lots_parent_fpo_lot_id', 'lots', ['parent_fpo_lot_id'], unique=False)
    op.create_table(
        'price_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crop_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('suggested_min_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('suggested_modal_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('suggested_max_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('data_source_tier', postgresql.ENUM('DISTRICT', 'STATE', 'NATIONAL_BASELINE', name='data_source_tier', create_type=False), nullable=False),
        sa.Column('data_freshness_days', sa.Integer(), nullable=False),
        sa.Column('explanation_summary', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 100', name='chk_prediction_confidence_range'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('suggested_min_price <= suggested_modal_price AND suggested_modal_price <= suggested_max_price', name='chk_price_prediction_spread'),
    )
    op.create_index('ix_price_predictions_lot_id', 'price_predictions', ['lot_id'], unique=False)
    op.create_index('ix_price_predictions_crop_id', 'price_predictions', ['crop_id'], unique=False)
    op.create_table(
        'sale_intents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expected_price_per_unit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('minimum_acceptable_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('available_from_date', sa.Date(), nullable=False),
        sa.Column('available_until_date', sa.Date(), nullable=False),
        sa.Column('allow_fpo_pooling', sa.Boolean(), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'SUSPENDED_POOLED', 'MATCHED', 'CLOSED', 'CANCELLED', name='sale_intent_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('available_until_date >= available_from_date', name='chk_sale_intent_date_bounds'),
        sa.CheckConstraint('expected_price_per_unit >= minimum_acceptable_price', name='chk_sale_intent_price_bounds'),
        sa.CheckConstraint('minimum_acceptable_price > 0', name='chk_sale_intent_min_price_positive'),
    )
    op.create_index('ix_sale_intents_lot_id', 'sale_intents', ['lot_id'], unique=True)
    op.create_table(
        'matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('buyer_demand_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_intent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('compatibility_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('distance_km', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sale_intent_id'], ['sale_intents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buyer_demand_id'], ['buyer_demands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('distance_km >= 0', name='chk_match_distance_positive'),
        sa.CheckConstraint('compatibility_score >= 0 AND compatibility_score <= 100', name='chk_match_score_range'),
        sa.UniqueConstraint('buyer_demand_id', 'sale_intent_id', name='uq_match_demand_intent'),
    )
    op.create_index('ix_matches_sale_intent_id', 'matches', ['sale_intent_id'], unique=False)
    op.create_index('ix_matches_buyer_demand_id', 'matches', ['buyer_demand_id'], unique=False)
    op.create_table(
        'offers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sale_intent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('buyer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seller_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('proposed_price_per_unit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('proposed_quantity', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'COUNTERED', 'ACCEPTED', 'REJECTED', 'EXPIRED', name='offer_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sale_intent_id'], ['sale_intents.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['seller_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('proposed_quantity > 0', name='chk_offer_quantity_positive'),
        sa.CheckConstraint('proposed_price_per_unit > 0', name='chk_offer_price_positive'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_offers_match_id', 'offers', ['match_id'], unique=False)
    op.create_index('ix_offers_buyer_id', 'offers', ['buyer_id'], unique=False)
    op.create_index('ix_offers_sale_intent_id', 'offers', ['sale_intent_id'], unique=False)
    op.create_index('ix_offers_seller_user_id', 'offers', ['seller_user_id'], unique=False)
    op.create_table(
        'negotiations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('offer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('counter_price_per_unit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('remarks', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['offer_id'], ['offers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.CheckConstraint('counter_price_per_unit > 0', name='chk_negotiation_price_positive'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_negotiations_offer_id', 'negotiations', ['offer_id'], unique=False)
    op.create_index('ix_negotiations_sender_user_id', 'negotiations', ['sender_user_id'], unique=False)
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('offer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('buyer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seller_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agreed_price_per_unit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_quantity', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('is_fpo_bulk_order', sa.Boolean(), nullable=False),
        sa.Column('order_status', postgresql.ENUM('CONFIRMED', 'DISPATCHED', 'DELIVERED', 'COMPLETED', 'CANCELLED', name='order_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['offer_id'], ['offers.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('total_amount > 0', name='chk_order_amount_positive'),
        sa.CheckConstraint('agreed_price_per_unit > 0', name='chk_order_price_positive'),
        sa.CheckConstraint('total_quantity > 0', name='chk_order_quantity_positive'),
    )
    op.create_index('ix_orders_offer_id', 'orders', ['offer_id'], unique=True)
    op.create_index('ix_orders_seller_id', 'orders', ['seller_id'], unique=False)
    op.create_index('ix_orders_buyer_id', 'orders', ['buyer_id'], unique=False)
    op.create_table(
        'grievances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filed_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('issue_category', postgresql.ENUM('QUALITY_DEFECT', 'WEIGHT_SHORTAGE', 'PAYMENT_DELAY', 'TRANSIT_DAMAGE', name='grievance_category', create_type=False), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED', name='grievance_status', create_type=False), nullable=False),
        sa.Column('admin_resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['filed_by_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_grievances_order_id', 'grievances', ['order_id'], unique=False)
    op.create_index('ix_grievances_filed_by_user_id', 'grievances', ['filed_by_user_id'], unique=False)
    op.create_table(
        'logistics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transporter_name', sa.String(length=150), nullable=False),
        sa.Column('vehicle_number', sa.String(length=30), nullable=False),
        sa.Column('driver_phone', sa.String(length=20), nullable=False),
        sa.Column('pickup_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivery_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tracking_status', postgresql.ENUM('PENDING_PICKUP', 'IN_TRANSIT', 'DELIVERED', name='logistics_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_logistics_order_id', 'logistics', ['order_id'], unique=True)
    op.create_table(
        'order_lot_allocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('allocated_quantity', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('member_share_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('payout_status', postgresql.ENUM('PENDING', 'DISBURSED', 'CONFIRMED_BY_FARMER', name='allocation_payout_status', create_type=False), nullable=False),
        sa.Column('disbursement_reference', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['farmer_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.CheckConstraint('allocated_quantity > 0', name='chk_allocation_quantity_positive'),
        sa.UniqueConstraint('order_id', 'lot_id', name='uq_order_lot_allocation'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('member_share_amount >= 0', name='chk_allocation_share_positive'),
    )
    op.create_index('ix_order_lot_allocations_farmer_user_id', 'order_lot_allocations', ['farmer_user_id'], unique=False)
    op.create_index('ix_order_lot_allocations_order_id', 'order_lot_allocations', ['order_id'], unique=False)
    op.create_index('ix_order_lot_allocations_lot_id', 'order_lot_allocations', ['lot_id'], unique=False)
    op.create_table(
        'payment_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_stage', postgresql.ENUM('ADVANCE', 'FINAL_SETTLEMENT', name='payment_stage', create_type=False), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('payment_method', postgresql.ENUM('BANK_TRANSFER', 'UPI', 'OFFLINE_CASH', 'FUTURE_RAZORPAY', name='payment_method', create_type=False), nullable=False),
        sa.Column('transaction_reference', sa.String(length=100), nullable=False),
        sa.Column('status', postgresql.ENUM('SUBMITTED', 'VERIFIED_BY_SELLER', 'DISPUTED', name='payment_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('amount > 0', name='chk_payment_amount_positive'),
    )
    op.create_index('ix_payment_records_order_id', 'payment_records', ['order_id'], unique=False)

def downgrade() -> None:
    # 1. Drop tables and their indexes in reverse dependency order
    op.drop_index('ix_payment_records_order_id', table_name='payment_records')
    op.drop_table('payment_records')
    op.drop_index('ix_order_lot_allocations_farmer_user_id', table_name='order_lot_allocations')
    op.drop_index('ix_order_lot_allocations_order_id', table_name='order_lot_allocations')
    op.drop_index('ix_order_lot_allocations_lot_id', table_name='order_lot_allocations')
    op.drop_table('order_lot_allocations')
    op.drop_index('ix_logistics_order_id', table_name='logistics')
    op.drop_table('logistics')
    op.drop_index('ix_grievances_order_id', table_name='grievances')
    op.drop_index('ix_grievances_filed_by_user_id', table_name='grievances')
    op.drop_table('grievances')
    op.drop_index('ix_orders_offer_id', table_name='orders')
    op.drop_index('ix_orders_seller_id', table_name='orders')
    op.drop_index('ix_orders_buyer_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_negotiations_offer_id', table_name='negotiations')
    op.drop_index('ix_negotiations_sender_user_id', table_name='negotiations')
    op.drop_table('negotiations')
    op.drop_index('ix_offers_match_id', table_name='offers')
    op.drop_index('ix_offers_buyer_id', table_name='offers')
    op.drop_index('ix_offers_sale_intent_id', table_name='offers')
    op.drop_index('ix_offers_seller_user_id', table_name='offers')
    op.drop_table('offers')
    op.drop_index('ix_matches_sale_intent_id', table_name='matches')
    op.drop_index('ix_matches_buyer_demand_id', table_name='matches')
    op.drop_table('matches')
    op.drop_index('ix_sale_intents_lot_id', table_name='sale_intents')
    op.drop_table('sale_intents')
    op.drop_index('ix_price_predictions_lot_id', table_name='price_predictions')
    op.drop_index('ix_price_predictions_crop_id', table_name='price_predictions')
    op.drop_table('price_predictions')
    op.drop_index('ix_lots_fpo_id', table_name='lots')
    op.drop_index('ix_lots_storage_location_pincode', table_name='lots')
    op.drop_index('ix_lots_farmer_user_id', table_name='lots')
    op.drop_index('ix_lots_crop_id', table_name='lots')
    op.drop_index('ix_lots_parent_fpo_lot_id', table_name='lots')
    op.drop_table('lots')
    op.drop_index('ix_fpo_memberships_farmer_user_id', table_name='fpo_memberships')
    op.drop_index('ix_fpo_memberships_fpo_id', table_name='fpo_memberships')
    op.drop_table('fpo_memberships')
    op.drop_index('ix_market_prices_district', table_name='market_prices')
    op.drop_index('ix_market_prices_price_date', table_name='market_prices')
    op.drop_index('ix_market_prices_crop_id', table_name='market_prices')
    op.drop_index('ix_market_prices_state', table_name='market_prices')
    op.drop_index('ix_market_prices_crop_district_date', table_name='market_prices')
    op.drop_table('market_prices')
    op.drop_index('ix_fpos_district', table_name='fpos')
    op.drop_index('ix_fpos_registration_number', table_name='fpos')
    op.drop_table('fpos')
    op.drop_index('ix_farmer_profiles_district', table_name='farmer_profiles')
    op.drop_index('ix_farmer_profiles_pincode', table_name='farmer_profiles')
    op.drop_index('ix_farmer_profiles_user_id', table_name='farmer_profiles')
    op.drop_table('farmer_profiles')
    op.drop_index('ix_buyer_profiles_user_id', table_name='buyer_profiles')
    op.drop_table('buyer_profiles')
    op.drop_index('ix_buyer_demands_buyer_id', table_name='buyer_demands')
    op.drop_index('ix_buyer_demands_delivery_destination_pincode', table_name='buyer_demands')
    op.drop_index('ix_buyer_demands_crop_id', table_name='buyer_demands')
    op.drop_table('buyer_demands')
    op.drop_index('ix_users_phone_number', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_pincode_coordinates_district', table_name='pincode_coordinates')
    op.drop_table('pincode_coordinates')
    op.drop_index('ix_crops_name', table_name='crops')
    op.drop_table('crops')

    # 2. Drop all 22 canonical PostgreSQL ENUM types
    grievance_status_enum.drop(op.get_bind(), checkfirst=True)
    grievance_category_enum.drop(op.get_bind(), checkfirst=True)
    payment_status_enum.drop(op.get_bind(), checkfirst=True)
    payment_method_enum.drop(op.get_bind(), checkfirst=True)
    payment_stage_enum.drop(op.get_bind(), checkfirst=True)
    logistics_status_enum.drop(op.get_bind(), checkfirst=True)
    allocation_payout_status_enum.drop(op.get_bind(), checkfirst=True)
    order_status_enum.drop(op.get_bind(), checkfirst=True)
    offer_status_enum.drop(op.get_bind(), checkfirst=True)
    buyer_demand_status_enum.drop(op.get_bind(), checkfirst=True)
    data_source_tier_enum.drop(op.get_bind(), checkfirst=True)
    sale_intent_status_enum.drop(op.get_bind(), checkfirst=True)
    lot_status_enum.drop(op.get_bind(), checkfirst=True)
    quality_grade_enum.drop(op.get_bind(), checkfirst=True)
    standard_unit_enum.drop(op.get_bind(), checkfirst=True)
    crop_category_enum.drop(op.get_bind(), checkfirst=True)
    verification_doc_type_enum.drop(op.get_bind(), checkfirst=True)
    buyer_category_enum.drop(op.get_bind(), checkfirst=True)
    fpo_membership_status_enum.drop(op.get_bind(), checkfirst=True)
    buyer_verification_status_enum.drop(op.get_bind(), checkfirst=True)
    farmer_kyc_status_enum.drop(op.get_bind(), checkfirst=True)
    user_role_enum.drop(op.get_bind(), checkfirst=True)
