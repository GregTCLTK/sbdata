import ast
import dataclasses
import json
import re
import sys
import typing

from sbdata.repo import find_item_by_name, Item
from sbdata.task import register_task, Arguments
from sbdata.wiki import get_wiki_sources_by_title


@dataclasses.dataclass
class DungeonDrop:
    item: Item
    floor: int
    chest: str
    drop_chances: dict[str, str]

    def get_drop_chance(self, has_s_plus: bool, talisman_level: int, boss_luck: int):
        drop_identifier = "S" + ('+' if has_s_plus else '') + 'ABCD'[talisman_level] + str(len([i for i in [0, 1, 3, 5, 10] if i >= boss_luck]))
        return self.drop_chances.get(drop_identifier)


@register_task("Fetch Dungeon Loot")
def fetch_dungeon_loot(args: Arguments):
    items = []
    for floor in get_wiki_sources_by_title(*[f'Template:Catacombs Floor {f} Loot Master' for f in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']]).values():
        for template in floor.filter_templates():
            if template.name.strip() == 'Dungeon Chest Table/Row':
                item = None
                ifloor = None
                chest = None
                drop_chances = {}

                for param in template.params:
                    attr_name = param.name.nodes[0].strip()
                    attr_value = param.value.nodes[0].strip()
                    if attr_name == 'item':
                        if item is None:
                            item = find_item_by_name(attr_value)
                    elif attr_name == 'customlink':
                        if item is None:
                            item = find_item_by_name(attr_value.split('#')[-1])
                    elif attr_name == 'chest':
                        chest = attr_value
                    elif attr_name == 'floor':
                        ifloor = int(attr_value)
                    elif attr_name.startswith("S"):
                        drop_chances[attr_name] = attr_value
                if item is None or ifloor is None or chest is None:
                    print('WARNING: Missing data for item: ' + str(template))
                else:
                    items.append(DungeonDrop(item, ifloor, chest, drop_chances))
    return items
