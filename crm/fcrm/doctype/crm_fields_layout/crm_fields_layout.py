# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.model.document import Document


class CRMFieldsLayout(Document):
	pass


@frappe.whitelist()
def get_fields_layout(doctype: str, type: str):
	tabs = []
	layout = None

	if frappe.db.exists("CRM Fields Layout", {"dt": doctype, "type": type}):
		layout = frappe.get_doc("CRM Fields Layout", {"dt": doctype, "type": type})

	if layout and layout.layout:
		tabs = json.loads(layout.layout)

	if not tabs:
		tabs = get_default_layout(doctype)

	has_tabs = tabs[0].get("sections") if tabs and tabs[0] else False

	if not has_tabs:
		tabs = [{"no_tabs": True, "sections": tabs}]

	allowed_fields = []
	for tab in tabs:
		for section in tab.get("sections"):
			if not section.get("fields"):
				continue
			allowed_fields.extend(section.get("fields"))

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldname in allowed_fields]

	for tab in tabs:
		for section in tab.get("sections"):
			for field in section.get("fields") if section.get("fields") else []:
				field = next((f for f in fields if f.fieldname == field), None)
				if field:
					field = {
						"label": _(field.label),
						"name": field.fieldname,
						"type": field.fieldtype,
						"options": getOptions(field),
						"mandatory": field.reqd,
						"read_only": field.read_only,
						"placeholder": field.get("placeholder"),
						"filters": field.get("link_filters"),
					}
					section["fields"][section.get("fields").index(field["name"])] = field

	return tabs or []


@frappe.whitelist()
def save_fields_layout(doctype: str, type: str, layout: str):
	if frappe.db.exists("CRM Fields Layout", {"dt": doctype, "type": type}):
		doc = frappe.get_doc("CRM Fields Layout", {"dt": doctype, "type": type})
	else:
		doc = frappe.new_doc("CRM Fields Layout")

	doc.update(
		{
			"dt": doctype,
			"type": type,
			"layout": layout,
		}
	)
	doc.save(ignore_permissions=True)

	return doc.layout


def get_default_layout(doctype: str):
	fields = frappe.get_meta(doctype).fields
	fields = [
		field.fieldname
		for field in fields
		if field.fieldtype not in ["Tab Break", "Section Break", "Column Break"]
	]

	return [{"no_tabs": True, "sections": [{"hideLabel": True, "fields": fields}]}]


def getOptions(field):
	if field.fieldtype == "Select" and field.options:
		field.options = field.options.split("\n")
		field.options = [{"label": _(option), "value": option} for option in field.options]
		field.options.insert(0, {"label": "", "value": ""})
	return field.options
