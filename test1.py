import pandas as pd
import google.generativeai as genai
import sys
import time

def setup_gemini(api_key):
    """제미나이 API를 설정합니다."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        print(f"제미나이 API 설정 오류: {e}")
        return None

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
    """질문과 선택지를 문자열로 생성합니다."""
    question_str = "\n" + "="*60 + "\n"
    question_str += f"질문: {row_data['Question']}\n"
    question_str += "-" * 60 + "\n"
    question_str += f"1. {row_data['Option 1']}\n"
    question_str += f"2. {row_data['Option 2']}\n"
    question_str += f"3. {row_data['Option 3']}\n"
    question_str += f"4. {row_data['Option 4']}\n"
    question_str += "="*60
    return question_str

def create_gemini_prompt(row_data):
    """제미나이를 위한 프롬프트를 생성합니다."""
    prompt = f"""다음 질문에 대한 답을 1, 2, 3, 4 중에서 선택해주세요. 다른 설명은 하지 말고 숫자만 답해주세요.

질문: {row_data['Question']}

1. {row_data['Option 1']}
2. {row_data['Option 2']}
3. {row_data['Option 3']}
4. {row_data['Option 4']}

답:"""
    return prompt

def ask_gemini(model, prompt, max_retries=3):
    """제미나이에게 질문하고 답변을 받습니다."""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            answer_text = response.text.strip()
            
            # 숫자만 추출
            for char in answer_text:
                if char in ['1', '2', '3', '4']:
                    return int(char)
            
            print(f"제미나이 응답에서 유효한 답을 찾을 수 없습니다: {answer_text}")
            return None
            
        except Exception as e:
            print(f"제미나이 API 호출 오류 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # 재시도 전 2초 대기
            else:
                return None

def main():
    csv_file = 'test_set.csv'
    
    print("제미나이 자동 답변 프로그램에 오신 것을 환영합니다!")
    
    # API 키 입력
    api_key = input("구글 제미나이 API 키를 입력하세요: ").strip()
    if not api_key:
        print("API 키가 필요합니다.")
        return
    
    # 제미나이 설정
    model = setup_gemini(api_key)
    if model is None:
        return
    
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
    print("제미나이가 질문에 답변하기 시작합니다...")
    
    # 결과 저장용
    results = []
    correct_answers = 0
    total_questions = 0
    api_errors = 0
    
    # 각 질문 처리
    for index, row in df.iterrows():
        print(f"\n진행률: {index + 1}/{len(df)}")
        
        # 질문 표시
        question_text = display_question(row)
        print(question_text)
        
        # 제미나이에게 질문
        prompt = create_gemini_prompt(row)
        print("\n🤖 제미나이가 생각 중...")
        
        gemini_answer = ask_gemini(model, prompt)
        
        if gemini_answer is None:
            print("❌ 제미나이 API 오류로 답변을 받을 수 없습니다.")
            api_errors += 1
            results.append({
                'Question': row['Question'],
                'Gemini_Answer': 'API_ERROR',
                'Correct_Answer': row.get('Answer', 'N/A'),
                'Is_Correct': False
            })
            continue
        
        total_questions += 1
        print(f"🤖 제미나이의 답변: {gemini_answer}번")
        
        # 정답 확인
        is_correct = False
        if 'Answer' in df.columns:
            correct_answer = row['Answer']
            if gemini_answer == correct_answer:
                print("✅ 정답입니다!")
                correct_answers += 1
                is_correct = True
            else:
                print(f"❌ 틀렸습니다. 정답은 {correct_answer}번입니다.")
        else:
            print("정답이 없어 정확성을 확인할 수 없습니다.")
        
        # 결과 저장
        results.append({
            'Question': row['Question'][:50] + '...' if len(row['Question']) > 50 else row['Question'],
            'Gemini_Answer': gemini_answer,
            'Correct_Answer': row.get('Answer', 'N/A'),
            'Is_Correct': is_correct
        })
        
        # API 호출 간격 조절 (Rate limit 방지)
        time.sleep(1)
    
    # 최종 결과 출력
    print(f"\n{'='*80}")
    print("최종 결과")
    print(f"{'='*80}")
    print(f"총 질문 수: {len(df)}")
    print(f"API 오류: {api_errors}개")
    print(f"답변 완료: {total_questions}개")
    
    if 'Answer' in df.columns and total_questions > 0:
        accuracy = (correct_answers / total_questions) * 100
        print(f"제미나이 정답 수: {correct_answers}")
        print(f"제미나이 정답률: {accuracy:.1f}%")
        
        # 상세 결과 표시
        print(f"\n{'='*80}")
        print("상세 결과")
        print(f"{'='*80}")
        for i, result in enumerate(results, 1):
            status = "✅" if result['Is_Correct'] else "❌"
            print(f"{i:2d}. {status} 질문: {result['Question']}")
            print(f"     제미나이: {result['Gemini_Answer']}번, 정답: {result['Correct_Answer']}번")
    
    print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()