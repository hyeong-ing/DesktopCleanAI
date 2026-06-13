import re

from scanner import scan_desktop_files, scan_destination_folders


def get_folder_names(destination_folders):
    """
    이동 목적지 폴더 Path 목록에서 폴더 이름만 꺼내는 함수

    예:
    [Path("school"), Path("project")]

    결과:
    {"school", "project"}
    """
    folder_names = set()

    for folder in destination_folders:
        folder_names.add(folder.name)

    return folder_names


def extract_front_tag(filename):
    """
    파일명 맨 앞에 있는 [태그]를 꺼내는 함수

    인정하는 형태:
    [school] 파일명.pdf
    [project] lotto.java

    인정하지 않는 형태:
    파일명 [school].pdf
    school 파일명.pdf
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

    조건:
    1. 파일명 맨 앞에 [태그]가 있어야 한다.
    2. 태그 이름과 실제 폴더 이름이 같아야 한다.
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


def classify_files_by_tag():
    """
    test_desktop 안의 파일들을 태그 기준으로 분류하는 함수
    """
    desktop_files = scan_desktop_files()
    destination_folders = scan_destination_folders()
    destination_folder_names = get_folder_names(destination_folders)

    results = []

    for file_path in desktop_files:
        result = classify_by_tag(file_path, destination_folder_names)

        if result is not None:
            results.append(result)

    return results


if __name__ == "__main__":
    results = classify_files_by_tag()

    print("파일명 태그 기반 추천 결과")
    print("----------------------")

    if not results:
        print("태그로 분류된 파일이 없습니다.")
    else:
        for result in results:
            print(
                f"{result['filename']} -> {result['targetFolder']} "
                f"/ 이유: {result['reason']}"
            )
