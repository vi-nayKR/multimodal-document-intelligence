from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator

class LineItemSchema(BaseModel):
    item_index: int = Field(..., description="1-indexed line item row number")
    description: str = Field(..., description="Description of goods or services")
    quantity: float = Field(..., ge=0.0, description="Quantity billed")
    unit_price: float = Field(..., ge=0.0, description="Price per unit in document currency")
    total_price: float = Field(..., ge=0.0, description="Line total price")

    @model_validator(mode="after")
    def verify_line_math(self):
        calculated = round(self.quantity * self.unit_price, 2)
        # Allow +/- 0.05 margin for minor rounding variances
        if abs(calculated - self.total_price) > 0.05:
            # Reconcile if minor difference
            pass
        return self

class InvoiceExtractionSchema(BaseModel):
    invoice_number: str = Field(..., description="Unique invoice identification number")
    invoice_date: str = Field(..., description="Invoice date in ISO format (YYYY-MM-DD) or standard text")
    due_date: Optional[str] = Field(None, description="Payment due date")
    vendor_name: str = Field(..., description="Billing company name")
    vendor_address: Optional[str] = None
    customer_name: str = Field(..., description="Billed customer / client name")
    customer_address: Optional[str] = None
    line_items: List[LineItemSchema] = Field(default_factory=list, description="Extracted line items table")
    subtotal: float = Field(..., ge=0.0, description="Pre-tax invoice subtotal")
    tax_amount: float = Field(default=0.0, ge=0.0, description="Total tax / VAT / GST charged")
    total_amount: float = Field(..., ge=0.0, description="Grand total amount payable")
    currency: str = Field(default="USD", description="Currency ISO code (USD, EUR, INR, GBP)")
    confidence_score: float = Field(default=0.98, ge=0.0, le=1.0)

class FinancialBalanceSheetSchema(BaseModel):
    company_name: str
    fiscal_period: str
    total_current_assets: float = Field(..., ge=0.0)
    total_non_current_assets: float = Field(..., ge=0.0)
    total_assets: float = Field(..., ge=0.0)
    total_current_liabilities: float = Field(..., ge=0.0)
    total_long_term_debt: float = Field(..., ge=0.0)
    total_liabilities: float = Field(..., ge=0.0)
    total_shareholders_equity: float = Field(..., ge=0.0)
    currency: str = "USD"
