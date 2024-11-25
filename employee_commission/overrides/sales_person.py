import frappe
from erpnext.setup.doctype.sales_person.sales_person import SalesPerson
from frappe.utils import flt
from erpnext import get_default_currency


class CustomSalesPerson(SalesPerson):
    def onload(self):
      super().onload()
      self.new_dashboard_info()
      self.calculate_commission()
      
    def new_dashboard_info(self):
        company_default_currency = get_default_currency()

        # Step 1: Fetch all non-return Sales Invoices with their grand_total
        sales_invoices = frappe.get_all(
            "Sales Invoice",
            filters={"is_return": 0, "docstatus": 1},
            fields=["name", "grand_total"]
        )

        # Step 2: Filter invoices based on the Sales Team relationship
        invoice_names = [
            si["name"]
            for si in sales_invoices
            if frappe.db.exists(
                "Sales Team",
                {"parent": si["name"], "sales_person": self.sales_person_name}
            )
        ]

        # Step 3: Sum the grand_total for these invoices
        allocated_amount_against_invoices = flt(sum(
            si["grand_total"] for si in sales_invoices if si["name"] in invoice_names
        ))

        
        sales_invoices_with_return = frappe.get_all(
            "Sales Invoice",
            filters={"is_return": 1, "docstatus": 1},
            fields=["name"]
        )

        return_invoice_names = [si["name"] for si in sales_invoices_with_return]
        
        allocated_amount_against_return = (flt(
            frappe.db.get_value(
                "Sales Team",
                {
                    "parenttype": "Sales Invoice",
                    "sales_person": self.sales_person_name,
                    "parent": ["in", return_invoice_names],
                    "docstatus": 1},
                "sum(allocated_amount)",
            ) or 0
        )*-1)
        
        allocated_amount_against_payments = flt(
            frappe.db.get_value(
                "Payment Entry",
                {"custom_sales_person": self.sales_person_name, "docstatus":1,},
                "sum(total_allocated_amount)",
            )or 0
        )
        
        new_info ={}
        new_info["allocated_amount_against_invoices"] = allocated_amount_against_invoices
        new_info["allocated_amount_against_return"] = allocated_amount_against_return
        new_info["allocated_amount_against_payments"] = allocated_amount_against_payments
        new_info["currency"] = company_default_currency
        
        self.set_onload("new_dashboard_info", new_info)
        
        
        
        
        
        
    def calculate_commission(self):
        
        # Step 1: Fetch all non-return Sales Invoices with their grand_total
        sales_invoices = frappe.get_all(
            "Sales Invoice",
            filters={"is_return": 0, "docstatus": 1 ,"posting_date": ["between", [self.custom_start_date, self.custom_end_date]]},
            fields=["name", "grand_total"]
        )

        # Step 2: Filter invoices based on the Sales Team relationship
        invoice_names = [
            si["name"]
            for si in sales_invoices
            if frappe.db.exists(
                "Sales Team",
                {"parent": si["name"], "sales_person": self.sales_person_name}
            )
        ]

        # Step 3: Sum the grand_total for these invoices
        allocated_amount_against_invoices = flt(sum(
            si["grand_total"] for si in sales_invoices if si["name"] in invoice_names
        ))

        
        sales_invoices_with_return = frappe.get_all(
            "Sales Invoice",
            filters={"is_return": 1, "docstatus": 1,"posting_date": ["between", [self.custom_start_date, self.custom_end_date]]},
            fields=["name"]
        )

        return_invoice_names = [si["name"] for si in sales_invoices_with_return]
        
        allocated_amount_against_return = (flt(
            frappe.db.get_value(
                "Sales Team",
                {
                    "parenttype": "Sales Invoice",
                    "sales_person": self.sales_person_name,
                    "parent": ["in", return_invoice_names],
                    "docstatus": 1},
                "sum(allocated_amount)",
            ) or 0
        )*-1)
        
        allocated_amount_against_payments = flt(
            frappe.db.get_value(
                "Payment Entry",
                {"custom_sales_person": self.sales_person_name, "docstatus":1,"posting_date":["between", [self.custom_start_date, self.custom_end_date]]},
                "sum(total_allocated_amount)",
            )or 0
        )
        
        
        
        self.custom_total_contribution_to_sales = allocated_amount_against_invoices
        self.custom_total_contribution_to_collection = allocated_amount_against_payments
        self.custom_total_contribution_to_return = allocated_amount_against_return
        
        
        self.custom_total_commission_of_sales = (self.custom_commission_rate_of_sales /100)*self.custom_total_contribution_to_sales
        self.custom_total_commission_of_collection = (self.custom_commission_rate_of_collection /100)*self.custom_total_contribution_to_collection
        self.custom_total_commission_of_return = (self.custom_commission_rate_of_return /100)*self.custom_total_contribution_to_return
        
        self.custom_total_commission = (self.custom_total_commission_of_sales + self.custom_total_commission_of_collection) - self.custom_total_commission_of_return



    
    