"""Synthetic showcase data on the exact retained QA host. No customer imports or sends.
Transport/session is injected by a private local runner; credentials are never stored here.
"""
import json,urllib.parse,datetime
COMPANY='Rimal Trading Demo'
PREFIX='[YOUSR DEMO] '
class Showcase:
 def __init__(self,session,base,state_path):
  assert base=='https://ads-paynow-qa-20261029.yousrerp.com'
  self.s=session;self.base=base;self.path=state_path
  try:self.state=json.load(open(state_path))
  except FileNotFoundError:self.state={'company':COMPANY,'created':[],'examples':{}}
 def save(self):
  import os
  fd=os.open(self.path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
  with os.fdopen(fd,'w') as f:json.dump(self.state,f,indent=2)
 def api(self,method,path,data=None,params=None):
  assert path.startswith('/api/')
  r=self.s.request(method,self.base+path,json=data,params=params,timeout=45,allow_redirects=False)
  if not r.ok:
   import os
   fd=os.open('/tmp/yousr-showcase-last-error.json',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
   with os.fdopen(fd,'w') as f:f.write(r.text)
   raise RuntimeError(f'{method} {path}: HTTP {r.status_code}; inspect private error')
  return r.json()
 def rows(self,dt,filters=None,fields=None):
  return self.api('GET','/api/resource/'+urllib.parse.quote(dt),params={'filters':json.dumps(filters or {}),'fields':json.dumps(fields or ['name']),'limit_page_length':500})['data']
 def get(self,dt,name):
  r=self.s.get(self.base+'/api/resource/'+urllib.parse.quote(dt)+'/'+urllib.parse.quote(name,safe=''),timeout=30)
  if r.status_code==404:return None
  assert r.ok,f'{dt} read {r.status_code}'
  return r.json()['data']
 def create(self,dt,doc,key=None):
  assert not doc.get('company') or doc['company']==COMPANY
  assert dt not in ['Email Account','Webhook','Notification','User','Payment Gateway Account']
  d=self.api('POST','/api/resource/'+urllib.parse.quote(dt),{'doctype':dt,**doc})['data'];self.state['created'].append({'doctype':dt,'name':d['name']})
  if key:self.state['examples'][key]={'doctype':dt,'name':d['name']}
  self.save();return d
 def ensure(self,dt,name,doc):
  return self.get(dt,name) or self.create(dt,doc)
 def foundation(self):
  self.ensure('Company',COMPANY,{'company_name':COMPANY,'abbr':'RTD','country':'Saudi Arabia','default_currency':'SAR','chart_of_accounts':'Standard'})
  self.ensure('Customer Group','Demo Customers',{'customer_group_name':'Demo Customers','parent_customer_group':'All Customer Groups','is_group':0})
  self.ensure('Supplier Group','Demo Suppliers',{'supplier_group_name':'Demo Suppliers','parent_supplier_group':'All Supplier Groups','is_group':0})
  for group in ['Office Furniture Demo','Technology Demo','Services Demo','Assembly Demo']:
   self.ensure('Item Group',group,{'item_group_name':group,'parent_item_group':'All Item Groups','is_group':0})
  customers=['Madar Offices Demo','Nawa Retail Demo','Rawasi Projects Demo','Layan Interiors Demo','Safa Clinics Demo','Waha Logistics Demo','Bayan Consulting Demo','Nour Education Demo','Rawa Hospitality Demo','Wasl Services Demo']
  for n in customers:self.ensure('Customer',n,{'customer_name':n,'customer_type':'Company','customer_group':'Demo Customers','territory':'All Territories'})
  suppliers=['Sahil Office Supply Demo','Madar Technology Supply Demo','Nawa Components Demo','Waha Services Supply Demo']
  for n in suppliers:self.ensure('Supplier',n,{'supplier_name':n,'supplier_group':'Demo Suppliers','supplier_type':'Company'})
  specs=[('DEMO-DESK','Ergonomic Desk','Office Furniture Demo',1450,850),('DEMO-CHAIR','Mesh Office Chair','Office Furniture Demo',680,360),('DEMO-CABINET','Steel Filing Cabinet','Office Furniture Demo',920,550),('DEMO-TABLE','Meeting Table','Office Furniture Demo',3200,1900),('DEMO-SHELF','Modular Shelf','Office Furniture Demo',480,260),('DEMO-LAPTOP','Business Laptop','Technology Demo',4200,3100),('DEMO-MONITOR','27-inch Monitor','Technology Demo',980,650),('DEMO-DOCK','USB-C Dock','Technology Demo',380,210),('DEMO-KEYBOARD','Wireless Keyboard','Technology Demo',190,90),('DEMO-HEADSET','Conference Headset','Technology Demo',260,130),('DEMO-DESKTOP','Desk Top Panel','Assembly Demo',250,160),('DEMO-FRAME','Desk Frame','Assembly Demo',400,260),('DEMO-KIT','Workstation Bundle','Assembly Demo',1950,1250),('DEMO-INSTALL','Workspace Installation','Services Demo',650,0),('DEMO-TRAINING','Team Training Session','Services Demo',1200,0),('DEMO-SUPPORT','Monthly Support Service','Services Demo',900,0)]
  self.state['catalogue']=[]
  for code,n,group,sell,buy in specs:
   self.ensure('Item',code,{'item_code':code,'item_name':n,'description':PREFIX+n+' — synthetic showcase item','item_group':group,'stock_uom':'Nos','is_stock_item':int(group!='Services Demo'),'is_sales_item':1,'is_purchase_item':1,'valuation_rate':buy,'standard_rate':sell,'item_defaults':[{'company':COMPANY,'default_warehouse':'Stores - RTD'}]})
   self.state['catalogue'].append({'code':code,'name':n,'sell':sell,'buy':buy,'stock':group!='Services Demo'})
   for pl,rate in [('Standard Selling',sell),('Standard Buying',buy)]:
    if rate and not self.rows('Item Price',{'item_code':code,'price_list':pl}):self.create('Item Price',{'item_code':code,'price_list':pl,'price_list_rate':rate,'currency':'SAR'})
  self.save();print(json.dumps({'company':COMPANY,'customers':len(customers),'suppliers':len(suppliers),'items':len(specs),'created':len(self.state['created'])}),flush=True)
 def submit(self,dt,name):
  d=self.get(dt,name);assert (d.get('company')==COMPANY or (dt=='Holiday List Assignment' and d.get('applicable_for')=='Company' and d.get('assigned_to')==COMPANY)) and any(x['doctype']==dt and x['name']==name for x in self.state['created'])
  if d['docstatus']==1:return d
  assert d['docstatus']==0
  return self.api('POST','/api/method/frappe.client.submit',{'doc':d})['message']
 def transaction(self,dt,key,doc,submit=True):
  prior=self.state['examples'].get(key)
  marker='BOT-0204:'+key
  if prior:d=self.get(dt,prior['name'])
  else:
   found=self.rows(dt,{'company':COMPANY,'custom_yousr_demo_reference':marker})
   assert len(found)<=1,'Duplicate demo marker requires review'
   if found:
    d=self.get(dt,found[0]['name']);self.state['examples'][key]={'doctype':dt,'name':d['name']}
    self.state['created'].append({'doctype':dt,'name':d['name']});self.save()
   else:
    assert key not in self.state.get('attempted',[]),'Uncertain creation requires operator reconciliation'
    self.state.setdefault('attempted',[]).append(key);self.save()
    d=self.create(dt,{'company':COMPANY,**doc,'custom_yousr_demo_reference':marker},key)
  return self.submit(dt,d['name']) if submit else d
 def scenarios(self):
  for dt in ['Stock Entry','Purchase Order','Purchase Receipt','Purchase Invoice','Sales Order','Delivery Note','Sales Invoice','Payment Entry']:
   name=dt+'-custom_yousr_demo_reference'
   self.ensure('Custom Field',name,{'dt':dt,'fieldname':'custom_yousr_demo_reference','label':'Demo Reference','fieldtype':'Data','length':140,'unique':1,'read_only':1,'no_copy':1,'print_hide':1,'insert_after':'company','is_system_generated':1})
  company=self.get('Company',COMPANY);accounts=self.rows('Account',{'company':COMPANY},['name','account_name','account_type','is_group'])
  def account(kind):return next(a['name'] for a in accounts if a['account_type']==kind and not a['is_group'])
  parent=next(a['name'] for a in accounts if a['is_group'] and a['account_name']=='Duties and Taxes')
  self.ensure('Account','Demo VAT 15% - RTD',{'account_name':'Demo VAT 15%','company':COMPANY,'parent_account':parent,'account_type':'Tax','tax_rate':15,'is_group':0})
  tax={'charge_type':'On Net Total','account_head':'Demo VAT 15% - RTD','description':'Demo VAT 15%','rate':15,'included_in_print_rate':0}
  self.ensure('Sales Taxes and Charges Template','Demo VAT 15% - RTD',{'title':'Demo VAT 15%','company':COMPANY,'taxes':[tax]})
  self.ensure('Purchase Taxes and Charges Template','Demo VAT 15% - RTD',{'title':'Demo VAT 15%','company':COMPANY,'taxes':[tax]})
  for name in ['Riyadh Showroom','Jeddah Distribution']:
   self.ensure('Warehouse',name+' - RTD',{'warehouse_name':name,'company':COMPANY,'is_group':0})
  opening=[{'item_code':i['code'],'qty':80+j*5,'t_warehouse':'Stores - RTD','basic_rate':i['buy'],'allow_zero_valuation_rate':0} for j,i in enumerate(self.state['catalogue']) if i['stock']]
  self.transaction('Stock Entry','opening-stock',{'stock_entry_type':'Material Receipt','purpose':'Material Receipt','posting_date':'2026-08-01','set_posting_time':1,'remarks':PREFIX+'Opening inventory for product showcase','items':opening})
  for k in range(6):
   date=f'2026-10-{3+k*3:02d}';supplier=['Sahil Office Supply Demo','Madar Technology Supply Demo','Nawa Components Demo'][k%3];item=self.state['catalogue'][k]
   po=self.transaction('Purchase Order',f'po-{k}',{'supplier':supplier,'transaction_date':date,'schedule_date':'2026-10-29','currency':'SAR','conversion_rate':1,'buying_price_list':'Standard Buying','taxes_and_charges':'Demo VAT 15% - RTD','taxes':[tax],'items':[{'item_code':item['code'],'qty':25+k*3,'rate':item['buy'],'schedule_date':'2026-10-29','warehouse':'Stores - RTD'}],'remarks':PREFIX+f'Procurement cycle {k+1}'})
   if k<4:
    pr=self.transaction('Purchase Receipt',f'pr-{k}',{'supplier':supplier,'posting_date':date,'set_posting_time':1,'currency':'SAR','conversion_rate':1,'taxes_and_charges':'Demo VAT 15% - RTD','taxes':[tax],'items':[{'item_code':item['code'],'qty':20,'rate':item['buy'],'warehouse':'Stores - RTD','purchase_order':po['name'],'purchase_order_item':po['items'][0]['name']}],'remarks':PREFIX+f'Receive purchase {k+1}'})
    self.transaction('Purchase Invoice',f'pi-{k}',{'supplier':supplier,'posting_date':date,'due_date':'2026-10-28','set_posting_time':1,'currency':'SAR','conversion_rate':1,'taxes_and_charges':'Demo VAT 15% - RTD','taxes':[tax],'items':[{'item_code':item['code'],'qty':20,'rate':item['buy'],'warehouse':'Stores - RTD','purchase_order':po['name'],'po_detail':po['items'][0]['name'],'purchase_receipt':pr['name'],'pr_detail':pr['items'][0]['name']}],'remarks':PREFIX+f'Supplier billing {k+1}'})
  customers=['Madar Offices Demo','Nawa Retail Demo','Rawasi Projects Demo','Layan Interiors Demo','Safa Clinics Demo','Waha Logistics Demo','Bayan Consulting Demo','Nour Education Demo','Rawa Hospitality Demo','Wasl Services Demo']
  for k in range(16):
   item=self.state['catalogue'][k%10];cust=customers[k%10];date=(datetime.date(2026,8,5)+datetime.timedelta(days=k*5)).isoformat()
   so=self.transaction('Sales Order',f'so-{k}',{'customer':cust,'transaction_date':date,'delivery_date':'2026-10-30','currency':'SAR','conversion_rate':1,'selling_price_list':'Standard Selling','taxes_and_charges':'Demo VAT 15% - RTD','taxes':[tax],'items':[{'item_code':item['code'],'qty':3+k%8,'rate':item['sell'],'delivery_date':'2026-10-30','warehouse':'Stores - RTD'}],'remarks':PREFIX+f'Workspace supply order {k+1}'})
   if k<12:
    dn=self.transaction('Delivery Note',f'dn-{k}',{'customer':cust,'posting_date':date,'set_posting_time':1,'currency':'SAR','conversion_rate':1,'selling_price_list':'Standard Selling','taxes_and_charges':'Demo VAT 15% - RTD','taxes':[tax],'items':[{'item_code':item['code'],'qty':3+k%8,'rate':item['sell'],'warehouse':'Stores - RTD','against_sales_order':so['name'],'so_detail':so['items'][0]['name']}],'remarks':PREFIX+f'Customer delivery {k+1}'})
    si=self.transaction('Sales Invoice',f'si-{k}',{'customer':cust,'posting_date':date,'due_date':(datetime.date.fromisoformat(date)+datetime.timedelta(days=30)).isoformat(),'set_posting_time':1,'currency':'SAR','conversion_rate':1,'selling_price_list':'Standard Selling','disable_rounded_total':1,'taxes_and_charges':'Demo VAT 15% - RTD','taxes':[tax],'items':[{'item_code':item['code'],'qty':3+k%8,'rate':item['sell'],'warehouse':'Stores - RTD','sales_order':so['name'],'so_detail':so['items'][0]['name'],'delivery_note':dn['name'],'dn_detail':dn['items'][0]['name']}],'remarks':PREFIX+f'Synthetic customer billing {k+1}'})
    if k<5:
     total=si['grand_total'];self.transaction('Payment Entry',f'payment-{k}',{'payment_type':'Receive','party_type':'Customer','party':cust,'posting_date':date,'paid_from':si['debit_to'],'paid_to':account('Cash'),'paid_amount':total,'received_amount':total,'source_exchange_rate':1,'target_exchange_rate':1,'reference_no':'DEMO-RECEIPT-'+str(k+1),'reference_date':date,'remarks':PREFIX+'Synthetic receipt; no external payment','references':[{'reference_doctype':'Sales Invoice','reference_name':si['name'],'allocated_amount':total}]})
  # Rich CRM pipeline without real email/phone destinations.
  for k,n in enumerate(['Madar Expansion','Nawa New Branch','Rawasi Fit-out','Layan Office Refresh','Safa Reception','Waha Dispatch Hub','Bayan Hybrid Office','Nour Training Centre','Rawa Guest Lounge','Wasl Field Team','Sahil Distribution','Rimal Partner Office']):
   prior=self.rows('Lead',{'lead_name':n+' Demo'})
   lead=self.get('Lead',prior[0]['name']) if prior else self.create('Lead',{'lead_name':n+' Demo','first_name':n+' Demo','company_name':n+' Demo','status':['Lead','Open','Interested','Opportunity'][k%4],'email_id':f'contact{k+1}@showcase.example.invalid'})
   if k<7 and not self.state['examples'].get(f'opp-{k}'):
    self.create('Opportunity',{'opportunity_from':'Lead','party_name':lead['name'],'company':COMPANY,'status':'Open','transaction_date':'2026-10-20','expected_closing':'2026-11-15','opportunity_amount':25000+k*8500,'probability':30+k*8,'currency':'SAR','title':n+' Demo'},f'opp-{k}')
  for k,title in enumerate(['Riyadh Office Rollout Demo','Jeddah Showroom Launch Demo','Warehouse Upgrade Demo']):
   prior=self.rows('Project',{'project_name':title})
   p=self.get('Project',prior[0]['name']) if prior else self.create('Project',{'project_name':title,'company':COMPANY,'customer':customers[k],'status':'Open','expected_start_date':'2026-10-01','expected_end_date':'2026-11-20','percent_complete':35+k*20,'estimated_costing':65000+k*12000})
   self.state['examples'][f'project-{k}']={'doctype':'Project','name':p['name']};self.save()
   for j,subject in enumerate(['Confirm requirements','Approve workspace layout','Procure furniture','Prepare equipment','Install and inspect','Train the team']):
    label=f'{subject} — {title}'
    if not self.rows('Task',{'subject':label}):self.create('Task',{'subject':label,'project':p['name'],'status':['Completed','Completed','Working','Open','Open','Open'][j],'priority':['High','Medium','High','Medium','Medium','Low'][j],'exp_start_date':f'2026-10-{5+j*3:02d}','exp_end_date':f'2026-11-{2+j*2:02d}','description':PREFIX+'Synthetic project task'})
  for k,subject in enumerate(['Set up a new warehouse','Understand receivables ageing','Import an opening item list','Add a purchasing approval step','Review a delivery discrepancy','Schedule team training']):
   key=f'issue-{k}'
   if not self.state['examples'].get(key):self.create('Issue',{'subject':subject+' — Demo','customer':customers[k],'status':['Open','Replied','Open','Resolved','Closed','Open'][k],'description':PREFIX+'Fictional support example. No external contact or notification.'},key)
  self.save();print(json.dumps({'examples':len(self.state['examples']),'created':len(self.state['created']),'company':COMPANY}),flush=True)
 def specialists(self):
  accounts=self.rows('Account',{'company':COMPANY},['name','account_name','account_type','is_group'])
  fixed=next(a['name'] for a in accounts if not a['is_group'] and a['account_type']=='Fixed Asset')
  self.ensure('Asset Category','Office Equipment Demo',{'asset_category_name':'Office Equipment Demo','enable_cwip_accounting':0,'accounts':[{'company_name':COMPANY,'fixed_asset_account':fixed}]})
  self.ensure('Location','Riyadh Demo Office',{'location_name':'Riyadh Demo Office'})
  for k,(code,name,amount) in enumerate([('DEMO-ASSET-LAPTOP','Finance Team Laptop',4800),('DEMO-ASSET-PRINTER','Office Multifunction Printer',7600),('DEMO-ASSET-DISPLAY','Meeting Room Display',5200)]):
   self.ensure('Item',code,{'item_code':code,'item_name':name,'item_group':'Technology Demo','stock_uom':'Nos','is_stock_item':0,'is_fixed_asset':1,'auto_create_assets':0,'asset_category':'Office Equipment Demo'})
   key=f'asset-{k}'
   if not self.state['examples'].get(key):self.create('Asset',{'item_code':code,'asset_name':name+' Demo','asset_category':'Office Equipment Demo','company':COMPANY,'location':'Riyadh Demo Office','purchase_date':'2026-08-01','available_for_use_date':'2026-08-05','gross_purchase_amount':amount,'net_purchase_amount':amount,'asset_quantity':1,'asset_type':'Existing Asset','calculate_depreciation':0},key)
  key='bom-workstation'
  if not self.state['examples'].get(key):self.create('BOM',{'company':COMPANY,'item':'DEMO-KIT','quantity':1,'currency':'SAR','conversion_rate':1,'is_active':1,'is_default':1,'rm_cost_as_per':'Price List','buying_price_list':'Standard Buying','items':[{'item_code':'DEMO-DESKTOP','qty':1,'rate':160},{'item_code':'DEMO-FRAME','qty':1,'rate':260},{'item_code':'DEMO-CHAIR','qty':1,'rate':360}]},key)
  bom=self.submit('BOM',self.state['examples'][key]['name'])
  if not self.state['examples'].get('work-order'):
   self.create('Work Order',{'company':COMPANY,'production_item':'DEMO-KIT','bom_no':bom['name'],'qty':12,'fg_warehouse':'Finished Goods - RTD','wip_warehouse':'Work In Progress - RTD','source_warehouse':'Stores - RTD','planned_start_date':'2026-11-02 09:00:00','description':PREFIX+'Assemble twelve customer workstations'},'work-order')
  for parameter in ['Surface finish','Assembly fit','Packaging condition']:self.ensure('Quality Inspection Parameter',parameter,{'parameter':parameter})
  template=self.ensure('Quality Inspection Template','Office Furniture Inspection Demo',{'quality_inspection_template_name':'Office Furniture Inspection Demo','item_quality_inspection_parameter':[{'specification':'Surface finish','numeric':0,'value':'No visible defects'},{'specification':'Assembly fit','numeric':0,'value':'Pass'},{'specification':'Packaging condition','numeric':0,'value':'Undamaged'}]})
  self.api('PUT','/api/resource/Item/DEMO-DESK',{'inspection_required_before_purchase':1,'quality_inspection_template':template['name']})
  if not self.state['examples'].get('quality-inspection'):
   pr=self.state['examples']['pr-0']['name'];self.create('Quality Inspection',{'inspection_type':'Incoming','reference_type':'Purchase Receipt','reference_name':pr,'item_code':'DEMO-DESK','sample_size':5,'inspected_by':'Administrator','report_date':'2026-10-03','status':'Accepted','quality_inspection_template':template['name'],'readings':[{'specification':'Surface finish','numeric':0,'value':'No visible defects','reading_value':'No visible defects','status':'Accepted'},{'specification':'Assembly fit','numeric':0,'value':'Pass','reading_value':'Pass','status':'Accepted'},{'specification':'Packaging condition','numeric':0,'value':'Undamaged','reading_value':'Undamaged','status':'Accepted'}],'remarks':PREFIX+'Five desks inspected: surface, stability and packaging.'},'quality-inspection')
  self.save();print(json.dumps({'specialists_ready':True,'examples':len(self.state['examples']),'created':len(self.state['created'])}),flush=True)
 def people(self):
  calendar=self.ensure('Holiday List','Demo Working Calendar 2026',{'holiday_list_name':'Demo Working Calendar 2026','from_date':'2026-01-01','to_date':'2026-12-31','weekly_off':'Friday','holidays':[]})
  old=self.rows('Holiday List Assignment',{'applicable_for':'Company','assigned_to':COMPANY,'holiday_list':calendar['name']})
  h=self.get('Holiday List Assignment',old[0]['name']) if old else self.create('Holiday List Assignment',{'applicable_for':'Company','assigned_to':COMPANY,'holiday_list':calendar['name'],'from_date':'2026-01-01'})
  if h['docstatus']==0:self.submit('Holiday List Assignment',h['name'])
  for d in ['Operations Demo','Sales Demo','Finance Demo','Delivery Demo']:
   self.ensure('Department',d+' - RTD',{'department_name':d,'company':COMPANY,'parent_department':'All Departments','is_group':0})
  for role in ['Operations Lead Demo','Sales Executive Demo','Finance Officer Demo','Warehouse Coordinator Demo']:
   self.ensure('Designation',role,{'designation_name':role})
  names=['Faisal','Noura','Omar','Reem','Saad','Lama','Yousef','Sara','Khalid','Hala','Rakan','Maha'];employees=[]
  roles=['Operations Lead Demo','Sales Executive Demo','Finance Officer Demo','Warehouse Coordinator Demo'];depts=['Operations Demo - RTD','Sales Demo - RTD','Finance Demo - RTD','Delivery Demo - RTD']
  for k,n in enumerate(names):
   full=n+' Demo';old=self.rows('Employee',{'first_name':n,'last_name':'Demo','company':COMPANY})
   e=self.get('Employee',old[0]['name']) if old else self.create('Employee',{'first_name':n,'last_name':'Demo','gender':'Female' if k%2 else 'Male','date_of_birth':'1992-06-15','date_of_joining':'2025-08-01','status':'Active','company':COMPANY,'department':depts[k%4],'designation':roles[k%4],'holiday_list':calendar['name'],'company_email':f'employee{k+1}@showcase.example.invalid','create_user_permission':0})
   employees.append(e);self.state['examples'][f'employee-{k}']={'doctype':'Employee','name':e['name']};self.save()
   for j in range(3):
    date=f'2026-10-{25+j:02d}'
    if not self.rows('Attendance',{'employee':e['name'],'attendance_date':date}):
     a=self.create('Attendance',{'employee':e['name'],'company':COMPANY,'attendance_date':date,'status':'Work From Home' if k%4==1 and j==2 else 'Present'});self.submit('Attendance',a['name'])
  for name,abbr,formula in [('Demo Basic Salary','DBS','base'),('Demo Housing Allowance','DHA','base * 0.25')]:
   self.ensure('Salary Component',name,{'salary_component':name,'salary_component_abbr':abbr,'type':'Earning','depends_on_payment_days':1,'amount_based_on_formula':1,'formula':formula,'is_tax_applicable':0})
  structure=self.ensure('Salary Structure','Demo Monthly Salary',{'name':'Demo Monthly Salary','company':COMPANY,'currency':'SAR','is_active':'Yes','payroll_frequency':'Monthly','earnings':[{'salary_component':'Demo Basic Salary','amount_based_on_formula':1,'formula':'base','depends_on_payment_days':1},{'salary_component':'Demo Housing Allowance','amount_based_on_formula':1,'formula':'base * 0.25','depends_on_payment_days':1}]})
  if structure['docstatus']==0:structure=self.submit('Salary Structure',structure['name'])
  for k,e in enumerate(employees[:3]):
   old=self.rows('Salary Structure Assignment',{'employee':e['name'],'salary_structure':structure['name']})
   assignment=self.get('Salary Structure Assignment',old[0]['name']) if old else self.create('Salary Structure Assignment',{'employee':e['name'],'salary_structure':structure['name'],'from_date':'2026-08-01','company':COMPANY,'currency':'SAR','base':9000+k*1500})
   if assignment['docstatus']==0:self.submit('Salary Structure Assignment',assignment['name'])
   key=f'salary-slip-{k}'
   if not self.state['examples'].get(key):self.create('Salary Slip',{'employee':e['name'],'company':COMPANY,'salary_structure':structure['name'],'start_date':'2026-10-01','end_date':'2026-10-31','posting_date':'2026-10-30','payroll_frequency':'Monthly','currency':'SAR','exchange_rate':1},key)
  self.save();print(json.dumps({'employees':len(employees),'salary_slips':3,'created':len(self.state['created'])}),flush=True)
