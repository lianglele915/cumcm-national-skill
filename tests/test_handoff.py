import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

WORK = Path(__file__).resolve().parents[1]
SCRIPT = WORK / 'skills/cumcm-national/scripts/validate_handoff.py'
spec = importlib.util.spec_from_file_location('handoff', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HandoffEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'result.csv').write_text('x,value\n1,2\n',encoding='utf-8')
        self.base = json.loads((SCRIPT.parents[1]/'assets/handoff-template.json').read_text(encoding='utf-8'))
        self.base.update(status='completed',pending=[],outputs=[self.artifact('result.csv')])

    def tearDown(self): self.temp.cleanup()

    def artifact(self,name):
        return {'path':name,'sha256':hashlib.sha256((self.root/name).read_bytes()).hexdigest(),'role':'test output'}

    def errors(self,data=None):return module.validate(data or self.base,self.root)

    def add_code(self,runner='vscode-task'):
        (self.root/'solve.py').write_text('print(2)\n',encoding='utf-8')
        (self.root/'run.log').write_text('2\nexit_code=0\n',encoding='utf-8')
        self.base['outputs'] += [self.artifact('solve.py'),self.artifact('run.log')]
        self.base['runs']=[{'command':'python solve.py','runtime':sys.executable,'cwd':'.','runner':runner,'exit_code':0,'log':'run.log'}]
        self.base['vscode_verification']={'status':'passed','evidence':['run.log']}

    def test_valid_analysis_artifact(self): self.assertEqual(self.errors(),[])
    def test_changed_data_hash_is_rejected(self):
        (self.root/'result.csv').write_text('changed',encoding='utf-8')
        self.assertTrue(any('mismatch' in e for e in self.errors()))
    def test_missing_file_is_rejected(self):
        (self.root/'result.csv').unlink();self.assertTrue(self.errors())
    def test_traversal_is_rejected(self):
        self.base['outputs'][0]['path']='../outside.csv'
        self.assertTrue(any('escapes' in e for e in self.errors()))
    def test_absolute_windows_path_is_rejected(self):
        self.base['outputs'][0]['path']='C:/outside.csv';self.assertTrue(self.errors())
    def test_cli_cannot_claim_vscode_success(self):
        self.add_code('cli');self.assertTrue(self.errors())
    def test_editor_evidence_is_accepted(self):
        self.add_code();self.assertEqual(self.errors(),[])
    def test_nonzero_exit_cannot_pass(self):
        self.add_code();self.base['runs'][0]['exit_code']=1;self.assertTrue(self.errors())
    def test_unhashed_log_is_rejected(self):
        self.add_code();self.base['outputs']=[x for x in self.base['outputs'] if x['path']!='run.log'];self.assertTrue(self.errors())
    def test_pending_or_failed_checks_prevent_completion(self):
        self.base['checks']=[{'status':'failed','name':'physical constraints'}];self.assertTrue(self.errors())
    def test_honest_partial_with_cli_is_accepted(self):
        self.add_code('cli');self.base.update(status='partial',pending=['VS Code verification outstanding'])
        self.base['vscode_verification']={'status':'cli_equivalent','evidence':['run.log']}
        self.assertEqual(self.errors(),[])
    def test_malformed_status_is_reported_not_crashed(self):
        self.base['vscode_verification']['status'] = ['invalid']
        self.assertTrue(self.errors())

    def test_cli_reports_failure_exit(self):
        self.base['outputs'][0]['sha256']='0'*64
        p=self.root/'handoff.json';p.write_text(json.dumps(self.base),encoding='utf-8')
        r=subprocess.run([sys.executable,'-X','utf8',str(SCRIPT),str(p),'--project-root',str(self.root)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(r.returncode,1);self.assertFalse(json.loads(r.stdout)['valid'])


if __name__=='__main__':unittest.main(verbosity=2)
