
import xml.etree.ElementTree as ET
import csv
from collections import defaultdict


def flatten_xml(element, path="", result=None):
    if result is None:
        result = {}

    current_path = f"{path}/{element.tag}"

    # Store text values
    text = (element.text or "").strip()
    if text:
        result[current_path + "/text()"] = text

    # Store attributes
    for name, value in element.attrib.items():
        result[f"{current_path}/@{name}"] = value

    # Distinguish repeated sibling elements
    counts = defaultdict(int)

    for child in element:
        counts[child.tag] += 1
        child_path = f"{current_path}/{child.tag}[{counts[child.tag]}]"
        flatten_xml_child(child, child_path, result)

    return result


def flatten_xml_child(element, path, result):
    result[path + "/#element"] = True

    text = (element.text or "").strip()
    if text:
        result[path + "/text()"] = text

    for name, value in element.attrib.items():
        result[f"{path}/@{name}"] = value

    counts = defaultdict(int)

    for child in element:
        counts[child.tag] += 1
        child_path = f"{path}/{child.tag}[{counts[child.tag]}]"
        flatten_xml_child(child, child_path, result)


def compare_xml(file1, file2):
    root1 = ET.parse(file1).getroot()
    root2 = ET.parse(file2).getroot()

    old = flatten_xml(root1)
    new = flatten_xml(root2)

    differences = []

    for path in sorted(set(old) | set(new)):
        old_value = old.get(path)
        new_value = new.get(path)

        if old_value == new_value:
            continue

        if path not in old:
            change = "Added"
        elif path not in new:
            change = "Removed"
        else:
            change = "Modified"

        differences.append({
            "XPath": path,
            "Change": change,
            "Old Value": old_value,
            "New Value": new_value
        })

    return differences


def export_csv(differences, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["XPath", "Change", "Old Value", "New Value"]
        )
        writer.writeheader()
        writer.writerows(differences)


if __name__ == "__main__":
    differences = compare_xml("map_old.xml", "map_new.xml")

    export_csv(differences, "xml_comparison.csv")

    print(f"Found {len(differences)} differences")
