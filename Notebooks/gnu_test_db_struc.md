#  Estructura de la base de datos:
Table account_account, columns=[
id	integer PRIMARY, 
create_date	timestamp(6),
write_date	timestamp(6),
create_uid	integer, 
write_uid	integer, 
reconcile	boolean, 
code	character, 
right	integer,
note	text, 
template	integer,
type	integer 
parent	integer, 
company	integer,	
active	boolean, 
second_currency	integer, 
name	character, 
deferral	boolean, 
left	integer,	
party_required	boolean,
general_ledger_balance	boolean, 
end_date	date, 	
replaced_by	integer, 	
start_date	date, 	
template_override	boolean,	
closed	boolean, 
debit_type	integer]


FOREIGN_KEYS=
type: account_account_type(id)	
parent: account_account(id)	
company: company_company(id)
second_currency: currency_currency(id)
replaced_by: account_account(id)
debit_type: account_account_type(id)
.