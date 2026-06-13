from scanner import get_desktop_path


def get_rules_path():
    """
    rules.txt 파일 경로를 가져오는 함수

    현재는 테스트용 Desktop 폴더 안의 .deskpilot/rules.txt를 사용한다.
    예:
    ~/Desktop/test_desktop/.deskpilot/rules.txt
    """
    return get_desktop_path() / ".deskpilot" / "rules.txt"


def read_rules():
    """
    rules.txt를 읽어서 파이썬 딕셔너리로 바꾸는 함수

    rules.txt 예:
    school: 정보처리기사, 서술형, 기사
    study: 스프링, 강의, 공부

    변환 결과:
    {
        "school": ["정보처리기사", "서술형", "기사"],
        "study": ["스프링", "강의", "공부"]
    }
    """
    rules_path = get_rules_path()

    if not rules_path.exists():
        return {}

    rules = {}

    with open(rules_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # 빈 줄은 건너뛴다.
            if line == "":
                continue

            # # 으로 시작하는 줄은 주석으로 보고 건너뛴다.
            if line.startswith("#"):
                continue

            # : 이 없으면 잘못된 규칙이므로 건너뛴다.
            if ":" not in line:
                continue

            folder_name, keywords_text = line.split(":", 1)

            folder_name = folder_name.strip()

            keywords = []

            for keyword in keywords_text.split(","):
                keyword = keyword.strip()

                if keyword != "":
                    keywords.append(keyword)

            if folder_name != "" and keywords:
                rules[folder_name] = keywords

    return rules


if __name__ == "__main__":
    rules = read_rules()

    print("rules.txt 읽기 결과")
    print("------------------")

    if not rules:
        print("규칙이 없습니다.")
    else:
        for folder_name, keywords in rules.items():
            print(f"{folder_name}: {keywords}")
