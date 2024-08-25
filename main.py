import logging
from collections import Counter
from math import ceil
from typing import Tuple, List

# TODO make 1 plate bending machine first, the update recipe list with more efficient recipes.

"""
Craft order:
- automatic compressor
- plate bending machine
- geothermal generator
"""

"""
Efficient updates:
- extruder for cables
- plate bender for red allow plates
- auto extractor for rubber from resin
"""

inventory = {
    "piston": 12,
    "iron_plate": 20,
}

# Mock database of crafting recipes
recipes = {
    "steel_plate": {
        "steel_ingot": 1
    },
    "iron_plate": {
        "iron_ingot": 1
    },
    "piston": {
        "planks": 3,
        "redstone": 1,
        "cobblestone": 4,
        "iron_ingot": 1
    },
    "red_alloy_ingot": {
        "redstone_dust": 4,
        "copper_ingot": 1
    },
    "red_allow_plate": {
        "red_alloy_ingot": 2
    },
    "copper_plate": {
        "copper_ingot": 1
    },
    "copper_cable": {
        "copper_plate": 0.5
    },
    "insulated_copper_cable": {
        "copper_cable": 1,
        "rubber": 1
    },
    "electronic_circuit": {
        "iron_plate": 1,
        "red_allow_plate": 2,
        "insulated_copper_cable": 6
    },
    "conveyor_module": {
        "electronic_circuit": 2,
        "glass": 3,
        "re_battery": 1,
        "iron_plate": 3
    },
    "tin_plate": {
        "tin_ingot": 1
    },
    "item_item_casing": {
      "tin_plate": 1
    },
    "tin_cable": {
        "tin_ingot": 1
    },
    "insulated_tin_cable": {
      "rubber": 1,
      "tin_cable": 1
    },
    "re_battery": {
        "item_item_casing": 4,
        "insulated_tin_cable": 1,
        "redstone": 2
    },
    "steel_machine_hull": {
        "steel_plate": 8
    },
    "auto_compressor": {
        "stone": 6,
        "electronic_circuit": 1,
        "steel_machine_hull": 1
    },
    "plate_bending_machine": {
        "piston": 4,
        "conveyor_module": 1,
        "electronic_circuit": 2,
        "auto_compressor": 2
    },
    "generator": {
        "re_battery": 1,
        "furnace": 1,
        "steel_machine_hull": 1
    },
    "iron_item_casing": {
        "iron_plate": 1
    },
    "geothermal_generator": {
        "glass": 4,
        "empty_cell": 2,
        "iron_item_casing": 2,
        "generator": 1
    }
}


#
# def build_dependency_graph():
#     graph = defaultdict(set)
#     for item, ingredients in recipes.items():
#         for ingredient in ingredients:
#             graph[ingredient].add(item)
#     return graph


def topological_sort(graph) -> List[str]:
    visited = set()
    order = []
    stack = set()  # Used to detect cycles

    graph = dict(graph)

    # Ensure all dependencies also have an entry in the graph
    for node, dependencies in list(graph.items()):
        for dependency in dependencies:
            if dependency not in graph:
                graph[dependency] = dict()

    def dfs(node):
        if node in stack:  # Cycle detected
            raise ValueError("The graph has a cycle!")

        if node not in visited:
            visited.add(node)
            stack.add(node)
            for neighbor in graph[node]:
                dfs(neighbor)
            order.append(node)
            stack.remove(node)

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node)

    return order


def merge_dicts(a, b) -> dict:
    merged_counter = Counter(a) + Counter(b)
    return dict(merged_counter)


def is_base_ingredient(item):
    return item not in recipes or len(recipes[item]) == 0


def try_use_inventory(inv, item, count) -> int:
    """
    Consumes items from the inventory.
    :param item:
    :param count:
    :return: How many of count if left, if the inventory was depleted for item.
    """
    if item not in inv:
        return count

    if count > inv[item]:
        insufficient = count - inv[item]
        consume = inv[item]
    else:
        insufficient = 0
        consume = count
    inv[item] -= consume
    return insufficient


def get_full_cost(item: str) -> dict[str, int]:
    """
    Recursively traverses recipes to get the full cost for an item including total intermediate items.
    :param item:
    :param count:
    :return:
    """
    items = dict()
    for d, n in recipes[item].items():
        # Use items from inventory first, if available.
        n = try_use_inventory(inventory, d, n)

        if n <= 0:
            continue

        if d not in items:
            items[d] = n
        else:
            # Merge with items, for if a dependency recipe already added this ingredient.
            items[d] += n
        if is_base_ingredient(d):
            continue
        for _ in range(ceil(n)):
            d_items = get_full_cost(d)
            items = merge_dicts(items, d_items)

    return items


def calculate_ingredients(item, count) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
    """
    Recursively calculate required intermediate recipes and required base items to craft `count` of `item`.
    :param item:
    :param count:
    :return: map of base item counts, and list of tuple of item and count
    """
    if item not in recipes:
        print(f"Could not find recipe for {item}")
        raise

    order = topological_sort(recipes)
    base_items = []
    craft_steps = []
    total_cost = dict()
    for _ in range(count):
        item_cost = get_full_cost(item)
        total_cost = merge_dicts(item_cost, total_cost)

    if item in total_cost:
        raise ValueError("Item can't depend on itself")
    total_cost[item] = count

    for i in order:
        if i not in total_cost:
            continue
        if is_base_ingredient(i):
            base_items.append((i, total_cost[i],))
        else:
            craft_steps.append((i, total_cost[i],))
    return base_items, craft_steps


def main():
    item_name = input("Enter the name of the item to craft: ")
    while not item_name.strip():
        item_name = input()
    item_count_str = input("Enter the count of the item: ")
    if item_count_str.strip():
        item_count = int(item_count_str)
    else:
        item_count = 1

    base_items, craft_steps = calculate_ingredients(item_name, item_count)

    print(f"\n[[ To Craft {item_count} {item_name} ]]")
    print("\nTotal Materials Needed:")
    for ingredient, count in base_items:
        print(f"  {ingredient}: {count}")
    print("\nCraft Order:")
    for recipe, count in craft_steps:
        print(f"  {ceil(count)}x {recipe}")


if __name__ == "__main__":
    while True:
        try:
            main()
            print("\n<<>> ================= <<>>")
        except:
            logging.exception("")
            pass
