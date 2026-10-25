"""Calculate editorial title scores. Does not infer scores or verify article facts."""
import argparse
import copy
import json
import math
from pathlib import Path
import sys

WEIGHTS = {'audience': 25, 'hook': 20, 'attention': 15,
           'shareability': 15, 'fidelity': 20, 'distinctiveness': 5}


def evaluate(candidates):
    if not isinstance(candidates, list) or not candidates:
        raise ValueError('candidates must be a non-empty list')
    ranked, rejected, ids, titles = [], [], set(), set()
    for original in candidates:
        if not isinstance(original, dict):
            raise ValueError('each candidate must be an object')
        item = copy.deepcopy(original)
        for key in ('id', 'title', 'angle'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'{key} must be a non-empty string')
            item[key] = item[key].strip()
        if item['id'] in ids or item['title'] in titles:
            raise ValueError('candidate IDs and titles must be unique')
        ids.add(item['id'])
        titles.add(item['title'])
        if type(item.get('grounded')) is not bool:
            raise ValueError('grounded must be an explicit boolean')
        for field in ('scores', 'rationales'):
            if not isinstance(item.get(field), dict) or set(item[field]) != set(WEIGHTS):
                raise ValueError(f'{field} must contain exactly the six rubric dimensions')
        for key, value in item['scores'].items():
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 5:
                raise ValueError(f'{key} score must be a finite number between 0 and 5')
            if value * 2 != int(value * 2):
                raise ValueError(f'{key} score must use half-point increments')
        if not all(isinstance(v, str) and v.strip() for v in item['rationales'].values()):
            raise ValueError('each score needs a non-empty rationale')
        evidence = item.get('evidence')
        if not isinstance(evidence, list) or not all(isinstance(e, str) and e.strip() for e in evidence):
            raise ValueError('evidence must be a list of non-empty strings')
        reasons = []
        if not item['grounded']:
            reasons.append('Article does not substantiate the title promise')
        if not evidence:
            reasons.append('No article evidence supplied')
        if item['scores']['fidelity'] < 3 or item['scores']['audience'] < 3:
            reasons.append('Insufficient content fidelity or audience relevance')
        if reasons:
            rejected.append({**item, 'rejection_reasons': reasons})
            continue
        item['contributions'] = {key: round(item['scores'][key] / 5 * weight, 2)
                                 for key, weight in WEIGHTS.items()}
        item['total'] = round(sum(item['scores'][key] / 5 * weight
                                  for key, weight in WEIGHTS.items()), 1)
        ranked.append(item)
    ranked.sort(key=lambda x: (-x['total'], -x['scores']['fidelity'], -x['scores']['audience']))
    recommended, angles = [], set()
    # Diversity is a tie-break among strong options, not a license to promote weak hooks.
    diversity_floor = ranked[min(2, len(ranked) - 1)]['total'] - 5 if ranked else 0
    for item in ranked:
        if item['total'] < diversity_floor:
            continue
        if item['angle'] not in angles:
            recommended.append(item)
            angles.add(item['angle'])
        if len(recommended) == 3:
            break
    for item in ranked:
        if len(recommended) == 3:
            break
        if item not in recommended:
            recommended.append(item)
    recommended.sort(key=lambda x: (-x['total'], -x['scores']['fidelity'], -x['scores']['audience']))
    return {'assessment_type': 'editorial_heuristic_not_measured_ctr', 'weights': WEIGHTS.copy(),
            'ranked': ranked, 'recommended': recommended, 'rejected': rejected,
            'needs_more_candidates': len(recommended) < 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding='utf-8-sig'))
        candidates = data.get('candidates') if isinstance(data, dict) else data
        result = evaluate(candidates)
        text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.output:
            args.output.write_text(text, encoding='utf-8')
        else:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            print(text, end='')
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
