import re
from pathlib import Path

from scanner import get_desktop_path, scan_desktop_files
from planner import build_move_plan


def remove_front_tag(filename):
    """
    파일명 맨 앞의 [태그]를 제거하는 함수

    예:
    [school]정보처리기사 정리본.pdf -> 정보처리기사 정리본.pdf
    [study] 결과화면_보라.png -> 결과화면_보라.png
    """
    cleaned_name = re.sub(r"^\[[^\]]+\]\s*", "", filename)

    # 혹시 태그를 제거했더니 빈 문자열이 되면 원래 파일명을 사용한다.
    if cleaned_name.strip() == "":
        return filename

    return cleaned_name.strip()


def make_unique_target_path(target_path, reserved_target_paths):
    """
    이동하려는 폴더 안에 같은 이름의 파일이 있으면
    파일명 뒤에 숫자를 붙여서 중복을 피하는 함수

    예:
    school/정리본.pdf 가 이미 있으면
    school/정리본(1).pdf 로 변경
    """
    candidate_path = target_path

    parent = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix

    number = 1

    while candidate_path.exists() or candidate_path in reserved_target_paths:
        candidate_filename = f"{stem}({number}){suffix}"
        candidate_path = parent / candidate_filename
        number += 1

    return candidate_path


def build_path_plan():
    """
    정리 미리보기 결과에 실제 이동 경로를 추가하는 함수

    추가되는 정보:
    - originalPath: 현재 파일 위치
    - targetPath: 이동될 예정 위치
    - targetFilename: 이동 후 파일명
    """
    desktop_path = get_desktop_path()

    move_plan = build_move_plan()
    desktop_files = scan_desktop_files()

    files_by_name = {}

    for file_path in desktop_files:
        files_by_name[file_path.name] = file_path

    path_plan = []

    # 같은 실행 안에서 중복 targetPath가 생기지 않도록 기록해두는 set
    reserved_target_paths = set()

    for item in move_plan:
        filename = item["filename"]
        source_path = files_by_name.get(filename)

        # 기존 item을 직접 바꾸지 않고 복사해서 사용한다.
        path_item = item.copy()

        if source_path is None:
            path_item["action"] = "KEEP"
            path_item["originalPath"] = None
            path_item["targetPath"] = None
            path_item["targetFilename"] = filename
            path_item["reason"] = "원본 파일을 찾을 수 없어 이동하지 않습니다."
            path_plan.append(path_item)
            continue

        path_item["originalPath"] = str(source_path)

        if item["action"] != "MOVE":
            path_item["targetPath"] = str(source_path)
            path_item["targetFilename"] = filename
            path_plan.append(path_item)
            continue

        target_folder_name = item["targetFolder"]
        target_folder_path = desktop_path / target_folder_name

        # 혹시 대상 폴더가 없으면 이동하지 않는다.
        if not target_folder_path.exists() or not target_folder_path.is_dir():
            path_item["action"] = "KEEP"
            path_item["targetPath"] = str(source_path)
            path_item["targetFilename"] = filename
            path_item["reason"] = "대상 폴더가 존재하지 않아 Desktop에 남깁니다."
            path_plan.append(path_item)
            continue

        # 파일명 앞의 [school], [study] 같은 태그를 제거한다.
        target_filename = remove_front_tag(filename)

        raw_target_path = target_folder_path / target_filename

        # 중복 파일명이 있으면 (1), (2) 형태로 변경한다.
        unique_target_path = make_unique_target_path(
            raw_target_path,
            reserved_target_paths,
        )

        reserved_target_paths.add(unique_target_path)

        path_item["targetPath"] = str(unique_target_path)
        path_item["targetFilename"] = unique_target_path.name

        path_plan.append(path_item)

    return path_plan


def print_path_plan(path_plan):
    """
    이동 경로 계획을 터미널에 출력하는 함수
    """
    print("이동 경로 미리보기")
    print("----------------")

    if not path_plan:
        print("정리할 파일이 없습니다.")
        return

    for item in path_plan:
        filename = item["filename"]
        action = item["action"]
        source = item["source"]
        reason = item["reason"]

        if action == "MOVE":
            print(f"[이동 예정] {filename}")
            print(f"  원본: {item['originalPath']}")
            print(f"  대상: {item['targetPath']}")
            print(f"  출처: {source}")
            print(f"  이유: {reason}")
            print()
        else:
            print(f"[남기기] {filename}")
            print(f"  위치: {item['originalPath']}")
            print(f"  출처: {source}")
            print(f"  이유: {reason}")
            print()


if __name__ == "__main__":
    path_plan = build_path_plan()
    print_path_plan(path_plan)
