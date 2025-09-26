import requests
import json
import pandas as pd
import os
import sys

# 설정
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer lm-studio" # 더미 API 키
}
CSV_FILE_PATH = "test.csv" # 파일 입력 모드에서 사용할 CSV 파일 경로

def get_current_model_name():
    """
    LM Studio에서 현재 사용 가능한 모델 목록을 가져와 첫 번째 모델의 ID를 반환합니다.
    """
    models_url = f"{LM_STUDIO_BASE_URL}/models"
    try:
        response = requests.get(models_url, headers=HEADERS)
        response.raise_for_status() # HTTP 오류 발생 시 예외 처리
        models_data = response.json()
        
        if models_data and 'data' in models_data and models_data['data']:
            model_id = models_data['data'][0]['id']
            print(f"✅ 현재 사용 중인 모델 ID: {model_id}")
            return model_id
        else:
            print("⚠️ LM Studio 서버에 로드된 모델이 없습니다.")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 오류: LM Studio 서버에 연결할 수 없습니다. 서버 주소를 확인하거나 LM Studio에서 서버를 시작하세요: {LM_STUDIO_BASE_URL}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 중 오류 발생: {e}")
        return None

def chat_completion(model_name, prompt):
    """
    LM Studio 모델에게 응답을 요청합니다.
    """
    chat_url = f"{LM_STUDIO_BASE_URL}/chat/completions"
    
    # OpenAI Chat Completions API 형식에 맞는 요청 페이로드
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1, # 객관식 문제 풀이를 위해 낮은 값 설정
        "max_tokens": 512
    }

    try:
        response = requests.post(chat_url, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()

        data = response.json()
        
        # 모델 응답 추출
        if data and 'choices' in data and data['choices']:
            return data['choices'][0]['message']['content'].strip()
        else:
            return "모델로부터 응답을 받지 못했습니다."

    except requests.exceptions.RequestException as e:
        return f"❌ 채팅 응답 요청 중 오류 발생: {e}"

## 모드 1: 사용자 직접 질문 모드
def run_interactive_mode(model_name):
    """
    사용자의 입력을 받아 실시간으로 모델에 질문하고 응답을 출력합니다.
    """
    print("\n[모드 1: 사용자 직접 질문 모드] (종료: 'quit')")
    
    while True:
        user_input = input("👤 당신: ")
        if user_input.lower() == 'quit':
            break
        
        bot_response = chat_completion(model_name, user_input)
        
        print(f"🤖 챗봇: {bot_response}")

## 모드 2: 파일 입력 모드
def run_file_mode(model_name):
    """
    test.csv 파일을 읽어와 객관식 질문을 생성하고 모델에 질의합니다.
    """
    print(f"\n[모드 2: 파일 입력 모드] - '{CSV_FILE_PATH}' 파일 처리 시작")
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ 오류: 지정된 파일 '{CSV_FILE_PATH}'을 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    try:
        # CSV 파일 로드
        df = pd.read_csv(CSV_FILE_PATH)
        required_columns = ['Question', 'Option 1', 'Option 2', 'Option 3', 'Option 4']
        
        # 필수 칼럼 확인
        if not all(col in df.columns for col in required_columns):
            print(f"❌ 오류: CSV 파일에 필요한 칼럼({', '.join(required_columns)}) 중 일부가 누락되었습니다.")
            return

        results = []
        
        for index, row in df.iterrows():
            question = row['Question']
            options = [
                row['Option 1'], row['Option 2'], row['Option 3'], row['Option 4']
            ]
            
            # 질문 및 선택지 포맷팅
            formatted_options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
            full_prompt = (
                f"다음 문제에 대해 가장 적절한 선택지 번호(1, 2, 3, 4 중 하나)만 출력하세요. "
                f"다른 설명은 필요 없습니다.\n\n"
                f"문제: {question}\n{formatted_options}"
            )

            print(f"\n--- [문제 {index+1}] ---")
            print(f"질의 내용:\n{question}\n{formatted_options}")
            
            # 모델 질의
            model_answer = chat_completion(model_name, full_prompt)
            
            print(f"🤖 모델 응답: {model_answer}")
            
            # 결과 저장
            results.append({
                'Question': question,
                'Model Answer': model_answer,
                # 필요하다면 다른 옵션 컬럼도 저장 가능
            })

        # 결과를 새로운 CSV 파일로 저장
        results_df = pd.DataFrame(results)
        output_file = "model_responses.csv"
        results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 파일 입력 모드 완료. 모델 응답이 '{output_file}'에 저장되었습니다.")

    except Exception as e:
        print(f"❌ 오류: 파일 처리 중 예상치 못한 오류 발생: {e}")


def main():
    print("🤖 LM Studio Chatbot 시작")
    
    # 1. 모델 이름 확인
    current_model = get_current_model_name()
    
    if not current_model:
        print("LM Studio 모델 서버에 연결할 수 없어 프로그램을 종료합니다.")
        return

    # 2. 실행 모드 선택
    print("\n--- 실행 모드 선택 ---")
    print("1. 사용자 직접 질문 모드")
    print("2. 파일 입력 모드 (test.csv)")
    
    while True:
        mode = input("모드 번호를 입력하세요 (1 또는 2): ")
        if mode == '1':
            run_interactive_mode(current_model)
            break
        elif mode == '2':
            run_file_mode(current_model)
            break
        else:
            print("잘못된 입력입니다. 1 또는 2를 입력해주세요.")
            
    print("👋 LM Studio 챗봇 프로그램이 종료되었습니다.")


if __name__ == "__main__":
    main()