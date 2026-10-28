# coding: utf-8
"""Offline CODESYS reconstruction. No target connection or download."""
from scriptengine import *
import os,json,traceback
root=os.environ.get('RBG_PROJECT_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
report={'scope':'offline only; no device access','success':False}
out=os.path.join(root,'evidence')
if not os.path.isdir(out):os.makedirs(out)
try:
    path=os.path.join(root,'RBG_WAGO_CC100_ModbusRTU.project')
    if os.path.exists(path):raise RuntimeError('Project exists. Use a fresh copy; no overwrite is allowed.')
    p=projects.create(path)
    p.add('CC100',4096,'1006 5004','6.4.6.11')
    app=p.find('Application',True)[0]
    lm=p.find('Library Manager',True)[0]
    for lib in ['WagoAppPlcModbus, 1.1.5.13 (WAGO)','WagoTypesCom, 1.6.2.3 (WAGO)','SysTime, 3.5.17.0 (System)']:
        lm.add_library(lib)
    with open(os.path.join(root,'source','objects.json')) as f:objects=json.load(f)
    for item in objects:
        if item['kind']=='dut':obj=app.create_dut(item['name'])
        elif item['kind']=='gvl':obj=app.create_gvl(item['name'])
        elif item['kind']=='fb':obj=app.create_function_block(item['name'])
        else:obj=app.create_program(item['name'])
        obj.textual_declaration.replace(item['declaration'])
        if item['kind'] in ('fb','program'):obj.textual_implementation.replace(item['implementation'])
    task=app.create_task_configuration().create_task('ModbusTask')
    task.interval='10';task.interval_unit='ms';task.pous.add('PLC_PRG')
    p.save();app.rebuild();app.generate_code()
    report['messages']=[unicode(m).encode('ascii','replace') for c in system.get_message_categories() for m in system.get_messages(c)]
    report['diagnostics']=[unicode(m.text).encode('ascii','replace') for m in system.get_message_objects()]
    assert not report['diagnostics'],'Compiler diagnostics require review'
    report['source_objects']=len(objects)
    p.save();p.close();report['success']=True
except:report['error']=traceback.format_exc()
with open(os.path.join(out,'offline_rebuild.json'),'w') as f:f.write(json.dumps(report,indent=2))
