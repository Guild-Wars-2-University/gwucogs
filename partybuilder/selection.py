import random
from itertools import combinations_with_replacement
from collections import Counter
from typing import Dict, List, Tuple, Set, Optional


def generate_optimized_team(
    players: Dict[str, Dict],
    roleset: Dict
) -> Tuple[Dict[str, Dict[str, Optional[str]]], Set[str]]:
    team_size = roleset['players']
    required = roleset['attributes']

    base_roles = {r: set(attrs) for r, attrs in roleset['roles'].items()}
    special_roles = roleset.get('special_roles', {})

    roles: Dict[str, Dict] = {}

    # Normal roles
    for r, attrs in base_roles.items():
        roles[r] = {
            "base": set([r]),
            "attributes": set(attrs),
            "eligible": [p for p, info in players.items() if r in info.get('roles', [])]
        }

    # Special role variants
    for sr, sinfo in special_roles.items():
        sr_attrs = set(sinfo.get('attributes', []))
        for base in sinfo.get('required_role', []):
            variant = f"{sr}__{base}"
            base_attrs = base_roles.get(base, set())
            roles[variant] = {
                "base": set([base, sr]),
                "attributes": base_attrs | sr_attrs,
                "eligible": [
                    p for p, info in players.items()
                    if sr in info.get('roles', []) and base in info.get('roles', [])
                ]
            }
            
    # Priority lookup, defaulting missing to 0, and min_prio for unassigned
    priority_map = {p: info.get('priority', 0) for p, info in players.items()}
    min_prio = max(priority_map.values(), default=0) + 1

    def combo_valid(combo):
        counter = Counter(combo)
        # early out if we don't have enough distinct players for any role
        if any(counter[r] > len(roles[r]["eligible"]) for r in counter):
            return False
        # count attributes covered by this combo
        attr_count = Counter(
            attr
            for r in combo
            for attr in roles[r]["attributes"]
            if attr in required
        )
        return all(attr_count[a] == required[a] for a in required)
    
    # Generate all role-multisets that satisfy the raw attribute needs
    available = [r for r in roles if roles[r]["eligible"]]
    combos = [
        combo
        for combo in combinations_with_replacement(available, team_size)
        if combo_valid(combo)
    ]

    def try_build(combo):
        assigned: Dict[str, str] = {}
        used: Set[str] = set()
        for r in combo:
            # sort candidates by (priority, random) to shuffle ties
            candidates = sorted(
                roles[r]["eligible"],
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

    def team_key(team: Dict[str, str]):
        attr_counter = Counter(
            attr
            for p, r in team.items()
            for attr in roles[r]["attributes"]
            if attr in required
        )
        mismatch = sum(abs(attr_counter[a] - required[a]) for a in required)
        prio_sum = sum(priority_map.get(p, min_prio) for p in team)
        return (mismatch, prio_sum, random.random())

    teams.sort(key=team_key)

    if teams:
        best_variants = teams[0]
        # Map to {player: {"base": ..., "special": ...}}
        best_structured = {
            p: roles[r]["base"]
            for p, r in best_variants.items()
        }
        leftovers = set(players) - set(best_variants)
        return best_structured, leftovers
    else:
        return {}, set(players)


def generate_multiple_teams(
    players: Dict[str, Dict],
    roleset: Dict
) -> Tuple[List[Dict[str, Dict[str, Optional[str]]]], Set[str]]:
    """
    Iteratively calls generate_optimized_team, removing used players each round,
    until no further valid team can be formed.
    Returns a list of all generated teams and the final leftover set.
    """
    all_teams: List[Dict[str, Dict[str, Optional[str]]]] = []
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
        "Akala":    {'priority': 0, 'roles': ["dps"]},
        "Vividus":  {'priority': 0, 'roles': ["dps", "adps", "aheal"]},
        "Kaela":    {'priority': 1, 'roles': ["dps", "qheal", "pylon"]},

        "Tharion":  {'priority': 1, 'roles': ["qdps", "dps"]},
        "Lyssara":  {'priority': 1, 'roles': ["aheal", "adps"]},
        "Corvan":   {'priority': 0, 'roles': ["pylon", "dps"]},
        "Serenya":  {'priority': 3, 'roles': ["qheal", "qdps"]},
        "Brenwick": {'priority': 1, 'roles': ["adps", "dps", "pylon"]},
        "Maelis":   {'priority': 0, 'roles': ["aheal", "qheal"]},
        "Orvyn":    {'priority': 1, 'roles': ["qdps", "adps"]},
        "Fiora":    {'priority': 0, 'roles': ["dps", "qheal"]},
        "Jorath":   {'priority': 1, 'roles': ["pylon", "qheal", "dps"]},
        "Selvara":  {'priority': 1, 'roles': ["aheal", "qdps", "adps"]},
        "Darian":   {'priority': 1, 'roles': ["qdps", "pylon", "dps"]},
        "Isolde":   {'priority': 1, 'roles': ["aheal", "adps", "qheal"]},
        "Kaelen":   {'priority': 0, 'roles': ["dps", "qdps"]},
        "Mirella":  {'priority': 1, 'roles': ["qheal", "pylon"]},
        "Torvak":   {'priority': 1, 'roles': ["adps", "dps"]},
        "Nyssa":    {'priority': 0, 'roles': ["aheal", "qheal", "qdps"]},
        "Rothric":  {'priority': 1, 'roles': ["pylon", "dps", "adps"]},
        "Elowen":   {'priority': 1, 'roles': ["qdps", "aheal"]},
        "Fenric":   {'priority': 1, 'roles': ["dps", "pylon"]},
        "Zerra":    {'priority': 0, 'roles': ["adps", "qdps", "aheal"]},
        "Halric":   {'priority': 1, 'roles': ["qheal", "pylon", "dps"]},
        "Ysolde":   {'priority': 1, 'roles': ["aheal", "adps", "qdps"]},
    }

    rolesets = {
        'standard': {
            'players': 5,
            'description': 'Standard 5-player squad.',
            'attributes': {
                'dps': 4,
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
            'players': 4,
            'description': 'debug only.',
            'attributes': {
                'heal': 1,
                'quick': 1,
                'alac': 1,
                'tank': 1,
            },
            'roles': {
                'adps': ['alac', 'dps'],
                'qdps': ['quick', 'dps'],
                'aheal': ['alac', 'heal'],
                'qheal': ['quick', 'heal'],
                'dps': ['dps']
            },
            'special_roles': {
                'tank': {'required_role': ['dps'], 'attributes': ['tank']}
            }
        },
        'Raid - Wing 7': {
            'players': 10,
            'description': 'Raid squad with pylon.',
            'attributes': {
                'dps': 8,
                'heal': 2,
                'quick': 2,
                'alac': 2,
                'pylon': 3
            },
            'roles': {
                'aheal': ['alac', 'heal'],
                'qheal': ['quick', 'heal'],
                'adps': ['alac', 'dps'],
                'qdps': ['quick', 'dps'],
                'dps': ['dps'],
            },
            'special_roles': {
                'pylon': {'required_role': ['dps', 'adps', 'qdps'], 'attributes': ['pylon']}
            }
        },
    }

    teams, not_used = generate_multiple_teams(players, rolesets['standard'])
    for idx, team in enumerate(teams, start=1):
        print(f"\nTeam {idx}:")
        for player, role_info in team.items():
            print(f"  {player}: {role_info}")
    print("\nLeftover players:", not_used)
