import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def candidate(index, score=4, angle=None):
    dimensions = ['audience', 'hook', 'attention', 'shareability', 'fidelity', 'distinctiveness']
    return {
        'id': str(index), 'title': f'Title {index}', 'angle': angle or f'angle-{index}',
        'grounded': True, 'evidence': ['Article paragraph 1: four workflow steps.'],
        'scores': {key: score for key in dimensions},
        'rationales': {key: 'Specific evidence supports this assessment.' for key in dimensions},
    }


class RankingTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('score_titles', ROOT / 'specs/personal/scripts/score_titles.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_weights_and_total(self):
        self.assertEqual(sum(self.module.WEIGHTS.values()), 100)
        self.assertEqual(self.module.evaluate([candidate(1, 4)])['ranked'][0]['total'], 80)

    def test_unsubstantiated_high_score_disqualified(self):
        false_claim = candidate(1, 5)
        false_claim['grounded'] = False
        result = self.module.evaluate([false_claim, candidate(2, 3)])
        self.assertEqual([x['id'] for x in result['recommended']], ['2'])
        self.assertEqual(result['rejected'][0]['id'], '1')

    def test_missing_evidence_disqualified(self):
        item = candidate(1)
        item['evidence'] = []
        self.assertFalse(self.module.evaluate([item])['recommended'])

    def test_invalid_scores_rejected(self):
        for value in [-1, 6, float('nan'), float('inf'), True, '5', 4.123456789]:
            with self.subTest(value=value):
                item = candidate(1)
                item['scores']['hook'] = value
                with self.assertRaises(ValueError):
                    self.module.evaluate([item])

    def test_no_silent_missing_dimension_or_reason(self):
        for field in ['scores', 'rationales']:
            item = candidate(1)
            del item[field]['hook']
            with self.assertRaises(ValueError):
                self.module.evaluate([item])

    def test_diverse_top_three_and_sorted_totals(self):
        result = self.module.evaluate([candidate(1, 5, 'benefit'), candidate(2, 4.5, 'benefit'),
                                       candidate(3, 4.5, 'story'), candidate(4, 4.5, 'contrast')])
        self.assertEqual([x['id'] for x in result['recommended']], ['1', '3', '4'])
        self.assertEqual([x['id'] for x in result['ranked']], ['1', '2', '3', '4'])

    def test_duplicates_and_empty_titles_fail(self):
        for items in [[candidate(1), candidate(1)], [dict(candidate(1), title=' ')]]:
            with self.assertRaises(ValueError):
                self.module.evaluate(items)

    def test_diversity_does_not_promote_a_much_weaker_title(self):
        weak = candidate(4, 1, 'story')
        weak['scores'].update(audience=3, fidelity=3)
        result = self.module.evaluate([candidate(1, 5, 'benefit'), candidate(2, 4.5, 'benefit'),
                                       candidate(3, 4, 'benefit'), weak])
        self.assertEqual([x['id'] for x in result['recommended']], ['1', '2', '3'])

    def test_not_enough_grounded_titles_no_fabricated_fill(self):
        result = self.module.evaluate([candidate(1)])
        self.assertEqual(len(result['recommended']), 1)
        self.assertTrue(result['needs_more_candidates'])

    def test_does_not_mutate_input(self):
        items = [candidate(1)]
        original = copy.deepcopy(items)
        self.module.evaluate(items)
        self.assertEqual(items, original)

    def test_cli_json_roundtrip_and_invalid_input(self):
        script = ROOT / 'specs/personal/scripts/score_titles.py'
        with tempfile.TemporaryDirectory() as tmp:
            inp, out = Path(tmp) / 'in.json', Path(tmp) / 'out.json'
            inp.write_text(json.dumps({'candidates': [candidate(i) for i in range(12)]}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(script), str(inp), '--output', str(out)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(json.loads(out.read_text(encoding='utf-8'))['recommended']), 3)
            inp.write_text('{}', encoding='utf-8')
            result = subprocess.run([sys.executable, str(script), str(inp)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)


class BuildTests(unittest.TestCase):
    def test_personal_sources_survive_rebuild_and_package_is_self_contained(self):
        reference = ROOT / 'specs/personal/assets/character-reference.png'
        original = reference.read_bytes()
        subprocess.run([sys.executable, str(ROOT / 'build.py')], check=True, capture_output=True)
        package = ROOT / 'skills/x-cover'
        self.assertEqual((package / 'assets/character-reference.png').read_bytes(), original)
        self.assertEqual(reference.read_bytes(), original)
        catalog = json.loads((package / 'references/style-catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog), 100)
        self.assertTrue(all(x['prompt_template'] and x['variables'] is not None for x in catalog))
        self.assertTrue((package / 'scripts/score_titles.py').exists())
        first = {str(p.relative_to(package)): p.read_bytes() for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        subprocess.run([sys.executable, str(ROOT / 'build.py')], check=True, capture_output=True)
        second = {str(p.relative_to(package)): p.read_bytes() for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
