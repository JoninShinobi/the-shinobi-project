"""
Finance Agent
Handles invoicing, payments, revenue tracking, and financial operations.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

from .base_agent import BaseAgent, AgentConfig, AgentResult


class FinanceAgent(BaseAgent):
    """
    Finance department agent responsible for:
    1. Invoice creation and management
    2. Payment tracking and reconciliation
    3. Revenue and commission calculations
    4. Expense management
    5. Financial reporting
    6. Stripe integration coordination
    """

    HUMAN_APPROVAL_THRESHOLD_GBP = 1000

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(
            name="FinanceAgent",
            description="Handles all financial operations including invoicing, payments, and reporting",
            config=config or AgentConfig(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                enable_tools=True,
                allowed_collections=[
                    "invoices", "payments", "revenue_tracking",
                    "expenses", "clients", "projects", "contracts"
                ]
            )
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Shinobi Finance Agent, responsible for all financial operations.

## Your Responsibilities
1. Invoice Management: Create, send, and track invoices
2. Payment Processing: Record payments, handle reconciliation
3. Revenue Tracking: Calculate commissions, track revenue by client/project
4. Expense Management: Log and categorize expenses
5. Financial Reporting: Generate financial summaries and reports

## Financial Rules
1. All amounts are in GBP (£)
2. Standard payment terms: Net 30
3. Late payment interest: 2% per month after 30 days
4. VAT rate: 20% (where applicable)
5. Human approval required for transactions over £1000

## Commission Structure
- Standard projects: 15% commission
- Retainer clients: 12% commission
- Referred clients: 20% commission (first project)

## Invoice Numbering
Format: INV-{YEAR}{MONTH}-{SEQUENTIAL}
Example: INV-202412-001

## Workflow Rules
1. Invoices over £1000 require human approval before sending
2. Payment reminders sent at: 7 days, 14 days, 21 days overdue
3. Escalate to human at 28 days overdue
4. All financial changes logged to audit_log

## Output Format
Always provide:
- Action summary
- Financial calculation breakdown
- Items requiring approval
- Next steps"""

    def build_task_prompt(self, context: dict) -> str:
        task_type = context.get("task_type", "general_finance")
        client_info = context.get("client", {})
        invoice_info = context.get("invoice", {})
        payment_info = context.get("payment", {})

        prompt = f"""## Finance Task
- Type: {task_type}
- Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        if client_info:
            prompt += f"""## Client Context
{json.dumps(client_info, indent=2)}

"""

        if invoice_info:
            prompt += f"""## Invoice Context
{json.dumps(invoice_info, indent=2)}

"""

        if payment_info:
            prompt += f"""## Payment Context
{json.dumps(payment_info, indent=2)}

"""

        prompt += f"""## Full Context
{json.dumps(context, indent=2)}

## Instructions
Execute the appropriate financial action.
Provide:
1. Action to be taken
2. Financial calculations (show work)
3. Items requiring human approval
4. Next steps and reminders"""

        return prompt

    def get_tools(self) -> List[Dict]:
        """Finance-specific tools"""
        return [
            {
                "name": "create_invoice",
                "description": "Create a new invoice",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "Client UUID"},
                        "project_id": {"type": "string", "description": "Project UUID (optional)"},
                        "line_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit_price_gbp": {"type": "number"},
                                    "vat_applicable": {"type": "boolean"}
                                }
                            }
                        },
                        "due_date": {"type": "string", "description": "Due date (ISO format)"},
                        "notes": {"type": "string", "description": "Invoice notes"}
                    },
                    "required": ["client_id", "line_items"]
                }
            },
            {
                "name": "record_payment",
                "description": "Record a payment received",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "invoice_id": {"type": "string", "description": "Invoice UUID"},
                        "amount_gbp": {"type": "number", "description": "Payment amount in GBP"},
                        "payment_method": {
                            "type": "string",
                            "enum": ["stripe", "bank_transfer", "cash", "cheque", "other"],
                            "description": "Payment method"
                        },
                        "payment_date": {"type": "string", "description": "Payment date"},
                        "reference": {"type": "string", "description": "Payment reference"}
                    },
                    "required": ["invoice_id", "amount_gbp", "payment_method"]
                }
            },
            {
                "name": "calculate_commission",
                "description": "Calculate commission on a project or payment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount_gbp": {"type": "number", "description": "Total amount"},
                        "commission_type": {
                            "type": "string",
                            "enum": ["standard", "retainer", "referral"],
                            "description": "Type of commission"
                        },
                        "project_id": {"type": "string", "description": "Related project"},
                        "team_member_id": {"type": "string", "description": "Team member for commission"}
                    },
                    "required": ["amount_gbp", "commission_type"]
                }
            },
            {
                "name": "generate_payment_reminder",
                "description": "Generate a payment reminder for overdue invoice",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "invoice_id": {"type": "string", "description": "Invoice UUID"},
                        "days_overdue": {"type": "integer", "description": "Number of days overdue"},
                        "reminder_level": {
                            "type": "string",
                            "enum": ["gentle", "firm", "final"],
                            "description": "Reminder tone level"
                        }
                    },
                    "required": ["invoice_id", "days_overdue"]
                }
            },
            {
                "name": "record_expense",
                "description": "Record a business expense",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount_gbp": {"type": "number", "description": "Expense amount"},
                        "category": {
                            "type": "string",
                            "enum": ["software", "hosting", "marketing", "travel", "equipment", "professional_services", "other"],
                            "description": "Expense category"
                        },
                        "description": {"type": "string", "description": "Expense description"},
                        "date": {"type": "string", "description": "Expense date"},
                        "project_id": {"type": "string", "description": "Related project (optional)"},
                        "receipt_file_id": {"type": "string", "description": "Receipt file UUID"}
                    },
                    "required": ["amount_gbp", "category", "description"]
                }
            },
            {
                "name": "get_financial_summary",
                "description": "Get financial summary for a period",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["this_month", "last_month", "this_quarter", "this_year", "custom"],
                            "description": "Time period"
                        },
                        "start_date": {"type": "string", "description": "Start date for custom period"},
                        "end_date": {"type": "string", "description": "End date for custom period"},
                        "client_id": {"type": "string", "description": "Filter by client (optional)"},
                        "project_id": {"type": "string", "description": "Filter by project (optional)"}
                    },
                    "required": ["period"]
                }
            }
        ]

    async def handle_tool_call(self, tool_name: str, tool_input: dict) -> Any:
        """Handle finance-specific tool calls"""
        self.log(f"Tool: {tool_name}")

        if tool_name == "create_invoice":
            return await self._create_invoice(tool_input)

        elif tool_name == "record_payment":
            return await self._record_payment(tool_input)

        elif tool_name == "calculate_commission":
            return await self._calculate_commission(tool_input)

        elif tool_name == "generate_payment_reminder":
            return await self._generate_payment_reminder(tool_input)

        elif tool_name == "record_expense":
            return await self._record_expense(tool_input)

        elif tool_name == "get_financial_summary":
            return await self._get_financial_summary(tool_input)

        return {"error": f"Unknown tool: {tool_name}"}

    async def _create_invoice(self, data: dict) -> dict:
        """Create an invoice"""
        line_items = data.get("line_items", [])

        # Calculate totals
        subtotal = sum(
            item.get("quantity", 1) * item.get("unit_price_gbp", 0)
            for item in line_items
        )

        vat_items = [i for i in line_items if i.get("vat_applicable", False)]
        vat_amount = sum(
            item.get("quantity", 1) * item.get("unit_price_gbp", 0) * 0.20
            for item in vat_items
        )

        total = subtotal + vat_amount
        requires_approval = total > self.HUMAN_APPROVAL_THRESHOLD_GBP

        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{datetime.now().strftime('%H%M%S')}"

        return {
            "success": True,
            "invoice_number": invoice_number,
            "client_id": data["client_id"],
            "subtotal_gbp": round(subtotal, 2),
            "vat_gbp": round(vat_amount, 2),
            "total_gbp": round(total, 2),
            "status": "draft",
            "requires_approval": requires_approval,
            "approval_reason": f"Invoice exceeds £{self.HUMAN_APPROVAL_THRESHOLD_GBP}" if requires_approval else None,
            "message": f"Invoice {invoice_number} created for £{round(total, 2)}"
        }

    async def _record_payment(self, data: dict) -> dict:
        """Record a payment"""
        payment_id = f"pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        amount = data.get("amount_gbp", 0)
        requires_approval = amount > self.HUMAN_APPROVAL_THRESHOLD_GBP

        return {
            "success": True,
            "payment_id": payment_id,
            "invoice_id": data["invoice_id"],
            "amount_gbp": amount,
            "payment_method": data["payment_method"],
            "status": "pending_verification" if requires_approval else "recorded",
            "requires_approval": requires_approval,
            "message": f"Payment of £{amount} recorded"
        }

    async def _calculate_commission(self, data: dict) -> dict:
        """Calculate commission based on type"""
        amount = data.get("amount_gbp", 0)
        commission_type = data.get("commission_type", "standard")

        rates = {
            "standard": 0.15,
            "retainer": 0.12,
            "referral": 0.20
        }

        rate = rates.get(commission_type, 0.15)
        commission = amount * rate

        return {
            "success": True,
            "gross_amount_gbp": amount,
            "commission_type": commission_type,
            "commission_rate": f"{int(rate * 100)}%",
            "commission_gbp": round(commission, 2),
            "net_amount_gbp": round(amount - commission, 2),
            "calculation": f"£{amount} × {int(rate * 100)}% = £{round(commission, 2)}"
        }

    async def _generate_payment_reminder(self, data: dict) -> dict:
        """Generate payment reminder content"""
        days_overdue = data.get("days_overdue", 0)

        if days_overdue <= 7:
            level = "gentle"
            subject = "Friendly Payment Reminder"
            urgency = "low"
        elif days_overdue <= 14:
            level = "gentle"
            subject = "Payment Reminder - Invoice Overdue"
            urgency = "medium"
        elif days_overdue <= 21:
            level = "firm"
            subject = "Payment Required - Invoice Overdue"
            urgency = "high"
        else:
            level = "final"
            subject = "Final Notice - Immediate Payment Required"
            urgency = "critical"

        return {
            "success": True,
            "invoice_id": data["invoice_id"],
            "days_overdue": days_overdue,
            "reminder_level": level,
            "suggested_subject": subject,
            "urgency": urgency,
            "escalate_to_human": days_overdue >= 28,
            "interest_applicable": days_overdue > 30,
            "interest_rate": "2% per month" if days_overdue > 30 else None
        }

    async def _record_expense(self, data: dict) -> dict:
        """Record an expense"""
        expense_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        amount = data.get("amount_gbp", 0)

        return {
            "success": True,
            "expense_id": expense_id,
            "amount_gbp": amount,
            "category": data["category"],
            "description": data["description"],
            "status": "recorded",
            "requires_receipt": amount > 25,
            "has_receipt": bool(data.get("receipt_file_id")),
            "message": f"Expense of £{amount} recorded in {data['category']}"
        }

    async def _get_financial_summary(self, data: dict) -> dict:
        """Get financial summary (placeholder - would query Directus)"""
        period = data.get("period", "this_month")

        # This would be replaced with actual Directus queries
        return {
            "success": True,
            "period": period,
            "summary": {
                "revenue_gbp": 0,
                "expenses_gbp": 0,
                "profit_gbp": 0,
                "outstanding_invoices_gbp": 0,
                "pending_payments_gbp": 0
            },
            "message": f"Financial summary for {period} - data would be fetched from Directus"
        }
