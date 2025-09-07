import random
import json
from itertools import combinations_with_replacement
from collections import Counter
from typing import Dict, List, Tuple, Set


def generate_optimized_team(
    players: Dict[str, Dict],
    roleset: Dict
) -> Tuple[Dict[str, str], Set[str]]:
    team_size = roleset['players']
    required = roleset['attributes']
    roles = {r: set(attrs) for r, attrs in roleset['roles'].items()}

    # Map each role to the list of players who can do it
    role_to_players = {
        r: [pname for pname, info in players.items() if r in info['roles']]
        for r in roles
    }

    # Priority lookup, defaulting missing to 0, and min_prio for unassigned
    priority_map = {p: info.get('priority', 0) for p, info in players.items()}
    min_prio = max(priority_map.values(), default=0) + 1

    def combo_valid(combo):
        counter = Counter(combo)
        # early out if we don't have enough distinct players for any role
        if any(counter[r] > len(role_to_players.get(r, [])) for r in counter):
            return False
        # count attributes covered by this combo
        attr_count = Counter(
            attr
            for r in combo
            for attr in roles[r]
            if attr in required
        )
        return all(attr_count[a] >= required[a] for a in required)

    # Generate all role-multisets that satisfy the raw attribute needs
    available = [r for r in roles if role_to_players.get(r)]
    combos = [
        combo
        for combo in combinations_with_replacement(available, team_size)
        if combo_valid(combo)
    ]

    def try_build(combo):
        assigned = {}
        used = set()
        for r in combo:
            # sort candidates by (priority, random) to shuffle ties
            candidates = sorted(
                role_to_players[r],
                key=lambda p: (priority_map.get(p, min_prio), random.random())
            )
            for p in candidates:
                if p not in used:
                    assigned[p] = r
                    used.add(p)
                    break
            else:
                return {}  # failed to fill this role
        return assigned if len(assigned) == team_size else {}

    # assemble every feasible team
    teams = [team for combo in combos if (team := try_build(combo))]

    # rank by (attribute mismatch, total priority, random tie-breaker)
    def team_key(team):
        attr_counter = Counter(
            attr
            for p, r in team.items()
            for attr in roles[r]
            if attr in required
        )
        mismatch = sum(abs(attr_counter[a] - required[a]) for a in required)
        prio_sum = sum(priority_map.get(p, min_prio) for p in team)
        return (mismatch, prio_sum, random.random())

    teams.sort(key=team_key)

    if teams:
        best = teams[0]
        leftovers = set(players) - set(best)
    else:
        best = {}
        leftovers = set(players)

    return best, leftovers


def generate_multiple_teams(
    players: Dict[str, Dict],
    roleset: Dict
) -> Tuple[List[Dict[str, str]], Set[str]]:
    """
    Iteratively calls generate_optimized_team, removing used players each round,
    until no further valid team can be formed.
    Returns a list of all generated teams and the final leftover set.
    """
    all_teams: List[Dict[str, str]] = []
    remaining_players = dict(players)

    while True:
        best, leftovers = generate_optimized_team(remaining_players, roleset)
        if not best:
            break

        all_teams.append(best)
        # Filter out used players for next iteration
        remaining_players = {p: players[p] for p in leftovers}

    return all_teams, leftovers

if __name__ == "__main__":
    # Example usage:
    players = {
        "Enaïra":   {'priority': 0, 'roles': ["dps", "adps", "aheal"]},
        "Akala":   {'priority': 0, 'roles': ["dps", "qheal", "qdps"]},
        "Vividus":    {'priority': 0, 'roles': ["dps", "adps", "aheal"]},
        "Kaela":    {'priority': 1, 'roles': ["dps", "adps"]},
    }

    rolesets = {
        'standard': {
            'players': 5,
            'description': 'Standard 5-player squad.',
            'attributes': {
                'dps': 0,
                'heal': 1,
                'quick': 1,
                'alac': 1
            },
            'roles': {
                'adps': ['alac', 'dps'],
                'qdps': ['quick', 'dps'],
                'aheal': ['alac', 'heal'],
                'qheal': ['quick', 'heal'],
                'dps': ['dps']
            }
        },
        'test': {
            'players': 2,
            'description': 'debug only.',
            'attributes': {
                'heal': 1,
                'quick': 1,
                'alac': 1
            },
            'roles': {
                'adps': ['alac', 'dps'],
                'qdps': ['quick', 'dps'],
                'aheal': ['alac', 'heal'],
                'qheal': ['quick', 'heal'],
                'dps': ['dps']
            }
        },
    }

    teams, not_used = generate_multiple_teams(players, rolesets['test'])
    for idx, team in enumerate(teams, start=1):
        print(f"Team {idx}:", team)
    print("Leftover players:", not_used)