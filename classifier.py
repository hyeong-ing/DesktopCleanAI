import re

from scanner import scan_desktop_files, scan_destination_folders
from rules import read_rules


def get_folder_names(destination_folders):
    """
    이동 목적지 폴더 Path 목록에서 폴더 이름만 꺼내는 함수
    """
    folder_names = set()

    for folder in destination_folders:
        folder_names.add(folder.name)

    return folder_names


def extract_front_tag(filename):
    """
    파일명 맨 앞에 있는 [태그]를 꺼내는 함수
    """
    pattern = r"^\[([^\]]+)\]"

    match = re.match(pattern, filename)

    if match is None:
        return None

    tag_name = match.group(1).strip()

    if tag_name == "":
        return None

    return tag_name


def classify_by_tag(file_path, destination_folder_names):
    """
    파일명 앞의 [태그]를 보고 이동할 폴더를 추천하는 함수
    """
    filename = file_path.name

    tag_name = extract_front_tag(filename)

    if tag_name is None:
        return None

    if tag_name not in destination_folder_names:
        return None

    return {
        "filename": filename,
        "targetFolder": tag_name,
        "reason": "파일명 앞 태그와 같은 이름의 폴더를 찾았습니다.",
        "source": "FILENAME_TAG",
    }


def classify_by_rules(file_path, rules, destination_folder_names):
    """
    rules.txt 규칙을 보고 이동할 폴더를 추천하는 함수

    조건:
    1. 파일명 안에 rules.txt의 키워드가 포함되어 있어야 한다.
    2. 규칙의 폴더 이름이 실제 이동 목적지 폴더에 존재해야 한다.
    """
    filename = file_path.name
    filename_lower = filename.lower()

    for folder_name, keywords in rules.items():
        # 실제 폴더가 없는 규칙은 사용하지 않는다.
        if folder_name not in destination_folder_names:
            continue

        for keyword in keywords:
            keyword_lower = keyword.lower()

            if keyword_lower in filename_lower:
                return {
                    "filename": filename,
                    "targetFolder": folder_name,
                    "reason": f"파일명에 rules.txt 키워드 '{keyword}'가 포함되어 있습니다.",
                    "source": "RULES_TXT",
                }

    return None


def classify_files():
    """
    test_desktop 안의 파일들을 분류하는 함수

    우선순위:
    1. 파일명 앞 [태그]
    2. rules.txt 키워드
    3. 아직 분류하지 않음
    """
    desktop_files = scan_desktop_files()
    destination_folders = scan_destination_folders()
    destination_folder_names = get_folder_names(destination_folders)
    rules = read_rules()

    results = []

    for file_path in desktop_files:
        # 1순위: 파일명 태그 기반 분류
        result = classify_by_tag(file_path, destination_folder_names)

        if result is not None:
            results.append(result)
            continue

        # 2순위: rules.txt 기반 분류
        result = classify_by_rules(file_path, rules, destination_folder_names)

        if result is not None:
            results.append(result)
            continue

    return results


if __name__ == "__main__":
    results = classify_files()

    print("파일 분류 추천 결과")
    print("----------------")

    if not results:
        print("분류된 파일이 없습니다.")
    else:
        for result in results:
            print(
                f"{result['filename']} -> {result['targetFolder']} "
                f"/ 출처: {result['source']} "
                f"/ 이유: {result['reason']}"
            )
