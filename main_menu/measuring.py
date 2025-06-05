import serial
import time

# 시리얼 포트 설정
def measuring():
    port = "COM3"  # 포트 이름
    baudrate = 9600  # 보드 레이트
    parity = serial.PARITY_EVEN  # 패리티 (짝수)
    bytesize = 7  # 데이터 비트 길이
    stopbits = serial.STOPBITS_ONE  # 정지 비트

    ser = serial.Serial(port, baudrate, parity=parity, bytesize=bytesize, stopbits=stopbits)

    def test(text):
        last_k_index = text.rfind("k")  # 마지막 k의 인덱스 찾기
        if last_k_index == -1:  # k가 없으면 -1 반환
            return -1, -1

        last_plus_index = text.rfind("+", 0, last_k_index)  # 마지막 k 이전의 + 인덱스 찾기
        return str(text[last_plus_index + 1:last_k_index])

    # 시리얼 포트 열기
    try:
        while True:  # while 루프 추가
            received_data = ser.read(ser.in_waiting).decode()
            print(received_data)
            if received_data:
                now = test(received_data[-50:])
                int(now.split(".")[0]) + float(now.split(".")[1])/1000
                return float(int(now.split(".")[0]) + float(now.split(".")[1])/1000)
            time.sleep(0.1)  # 짧은 지연 시간 추가
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
    except Exception as e:  # 다른 예외 발생 시 출력
        print(f"오류 발생: {e}")
        return 0
    finally:
        # 시리얼 포트 닫기
        ser.close()

print(measuring())