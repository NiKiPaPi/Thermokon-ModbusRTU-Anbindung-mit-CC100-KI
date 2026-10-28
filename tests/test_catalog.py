import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = json.loads((ROOT/'docs'/'registers_revm.json').read_text())


class CatalogTest(unittest.TestCase):
    def test_addresses_and_complete_documented_spaces(self):
        actual={(r['fc'],r['address']) for r in ROWS}
        expected={(3,a) for a in range(40)} | {(3,a) for a in range(0x100,0x112)}
        expected|={(3,a) for a in range(0x200,0x208)} | {(3,0x4000),(3,0x4001)}
        expected|={(1,a) for a in range(14)} | {(1,a) for a in range(0x100,0x105)}
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual),len(ROWS))

    def test_humidity_and_reserved_excluded(self):
        excluded={(3,a) for a in [8,21,27,29,30,0x105,0x201]}
        excluded|={(1,a) for a in [1,2,7,10,11]}
        self.assertEqual({(r['fc'],r['address']) for r in ROWS if not r['supported']},excluded)

    def test_read_only_identity_and_side_effects(self):
        bykey={(r['fc'],r['address']):r for r in ROWS}
        self.assertEqual(bykey[3,0]['access'],'RO')
        self.assertEqual(bykey[3,1]['access'],'RO')
        for a in [0x101,0x10F,0x110]: self.assertTrue(bykey[3,a]['read_clears'])

    def test_no_write_function_codes(self):
        self.assertTrue(all(r['fc'] in [1,3] for r in ROWS))
        source=(ROOT/'source'/'FB_Thermokon_ModbusScanner.st').read_text()
        for fc in ['5','6','15','16','22','23']:
            self.assertNotIn('query.bFunctionCode:='+fc+';',source)
        self.assertIn('query.uiWriteQuantity:=0;',source)

    def test_manual_examples(self):
        byname={r['name']:r for r in ROWS}
        def value(name, raw):
            r=byname[name]
            if r['signed'] and raw>=32768: raw-=65536
            return raw*r['scale']
        self.assertAlmostEqual(value('Raumtemperatur',184),18.4)
        self.assertAlmostEqual(value('Lokaler_Sollwertoffset',0xFFE7),-2.5)
        self.assertAlmostEqual(value('Regler_Heizen',1023),100)
        self.assertAlmostEqual(value('AO1_Spannung',500),5)
        self.assertAlmostEqual(value('Handwert_AO1',1000),100)


if __name__=='__main__': unittest.main(verbosity=2)
