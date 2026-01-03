import cv2

# 딸기 분류기 로드
strawberry_cascade = cv2.CascadeClassifier('/home/juby/strb/strawberry_classifier.xml')

# 웹캠 객체 생성
cap = cv2.VideoCapture(0)  # 0은 기본 웹캠
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if cap.isOpened():  # 캡처 객체 초기화 확인
    while True:
        ret, img = cap.read()  # 다음 프레임 읽기
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 회색조 변경
        if ret:  # 프레임 읽기 정상
            strawberries = strawberry_cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=5)

            # 인식된 딸기에 사각형 그리기
            for (x, y, w, h) in strawberries:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 초록색 사각형

            # 결과 영상 표시
            cv2.imshow('camera', img)
            
            if cv2.waitKey(1) != -1:  # 화면에 표시
                break
        else:
            print('no frame')  # 다음 프레임을 읽을 수 없음.
            break
else:
    print("Can't open video.")  # 캡처 객체 초기화 실패

cap.release()  # 캡쳐 자원 반납
cv2.destroyAllWindows()
