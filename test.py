import pandas as pd
import sys

def load_questions(csv_file):
    """CSV 파일에서 질문 데이터를 로드합니다."""
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        print(f"오류: '{csv_file}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return None

def display_question(row_data):
    """질문과 선택지를 화면에 표시합니다."""
    print("\n" + "="*60)
    print(f"질문: {row_data['Question']}")
    print("-" * 60)
    print(f"1. {row_data['Option 1']}")
    print(f"2. {row_data['Option 2']}")
    print(f"3. {row_data['Option 3']}")
    print(f"4. {row_data['Option 4']}")
    print("="*60)

def get_user_answer():
    """사용자의 답변을 입력받습니다."""
    while True:
        try:
            answer = input("\n답을 선택하세요 (1-4, 'q'로 종료): ").strip().lower()
            if answer == 'q':
                return 'quit'
            elif answer in ['1', '2', '3', '4']:
                return int(answer)
            else:
                print("잘못된 입력입니다. 1, 2, 3, 4 중에서 선택하거나 'q'를 입력하세요.")
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            return 'quit'

def main():
    csv_file = 'test_set.csv'
    
    print("CSV 질문 프로그램에 오신 것을 환영합니다!")
    print(f"'{csv_file}' 파일에서 질문을 불러오는 중...")
    
    # CSV 파일 로드
    df = load_questions(csv_file)
    if df is None:
        return
    
    # 필수 컬럼 확인
    required_columns = ['Question', 'Option 1', 'Option 2', 'Option 3', 'Option 4']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"오류: 다음 컬럼이 CSV 파일에 없습니다: {missing_columns}")
        print(f"현재 파일의 컬럼: {list(df.columns)}")
        return
    
    print(f"총 {len(df)}개의 질문을 불러왔습니다.")
    print("질문을 시작합니다. ('q'를 입력하면 언제든 종료할 수 있습니다.)")
    
    # 각 질문 처리
    correct_answers = 0
    total_questions = 0
    2
    for index, row in df.iterrows():
        question_text = display_question(row)
        print(question_text)
        
        user_answer = get_user_answer()
        if user_answer == 'quit':
            break
        
        total_questions += 1
        
        # 정답이 있는 경우 확인 (Answer 컬럼이 있다면)
        if 'Answer' in df.columns:
            correct_answer = row['Answer']
            if user_answer == correct_answer:
                print("✅ 정답입니다!")
                correct_answers += 1
            else:
                print(f"❌ 틀렸습니다. 정답은 {correct_answer}번입니다.")
        else:
            print(f"선택하신 답: {user_answer}번")
        
        # 다음 질문으로 넘어갈지 확인
        if index < len(df) - 1:
            continue_choice = input("\n다음 질문으로 넘어가시겠습니까? (Enter로 계속, 'q'로 종료): ").strip().lower()
            if continue_choice == 'q':
                break
    
    # 결과 출력
    if total_questions > 0:
        print(f"\n{'='*60}")
        print("결과 요약")
        print(f"{'='*60}")
        print(f"총 질문 수: {total_questions}")
        if 'Answer' in df.columns:
            print(f"정답 수: {correct_answers}")
            print(f"정답률: {(correct_answers/total_questions)*100:.1f}%")
        print("프로그램을 종료합니다. 수고하셨습니다!")

if __name__ == "__main__":
    main()