from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/cumcm-national'


class ResourceTests(unittest.TestCase):
    def test_relative_references_are_available(self):
        for file in SKILL.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((file.parent / target.split('#')[0]).is_file(), f'{file.name}: {target}')

    def test_provenance_deduplication_and_files(self):
        manifest = json.loads((SKILL/'references/source-manifest.json').read_text(encoding='utf-8'))
        pdfs = [r for r in manifest['sources'] if r['format']=='pdf']
        self.assertEqual(len(pdfs),manifest['pdf_files'])
        self.assertEqual(len({r['sha256'] for r in pdfs}),manifest['unique_pdf_contents'])
        for source in manifest['sources']:
            self.assertTrue((SKILL.parent.parent/source['used_in']).is_file() if source['used_in'].startswith('skills/') else (SKILL/source['used_in']).is_file())
            self.assertRegex(source['sha256'],r'^[a-f0-9]{64}$')
        for file in SKILL.rglob('*.json'):
            json.loads(file.read_text(encoding='utf-8'))


if __name__ == '__main__': unittest.main(verbosity=2)
