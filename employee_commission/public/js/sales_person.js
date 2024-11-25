frappe.ui.form.on("Sales Person", {
  refresh: function (frm) {
    if (frm.doc.__onload && frm.doc.__onload.new_dashboard_info) {
      let new_info = frm.doc.__onload.new_dashboard_info;

      frm.dashboard.add_indicator(
        __("Total Contribution Amount Against Invoices: {0}", [
          format_currency(
            new_info.allocated_amount_against_invoices,
            new_info.currency
          ),
        ]),
        "blue"
      );

      frm.dashboard.add_indicator(
        __("Total Contribution Amount Against Return: {0}", [
          format_currency(
            new_info.allocated_amount_against_return,
            new_info.currency
          ),
        ]),
        "red"
      );

      frm.dashboard.add_indicator(
        __("Total Contribution Amount Against Collection: {0}", [
          format_currency(
            new_info.allocated_amount_against_payments,
            new_info.currency
          ),
        ]),
        "green"
      );
    }
    console.log("Custom refresh logic for Sales Person executed");
    if (!frm.doc.__onload.new_dashboard_info) {
      console.warn("No new dashboard info loaded for Sales Person");
    }
  },
});
