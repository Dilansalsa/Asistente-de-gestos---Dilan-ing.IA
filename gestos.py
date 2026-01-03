import cv2
import mediapipe as mp
import os
import time
import pyautogui 
import math

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)
cap.set(3, 1280) 
cap.set(4, 720)

acciones = {
    1: ["chrome", "start chrome"],
    2: ["calculadora", "calc"],
    3: ["bloc notas", "notepad"],
    4: ["ChatGPT", "start https://chatgpt.com"], 
    5: ["foto guardada", "screenshot"] 
}
gesto_actual = 0
contador_frames = 0
FRAMES_PARA_ACTIVAR = 30
accion_ejecutada = False 
tipsIds = [8, 12, 16, 20]

print("Asistente de gestos")
print("1 dedo: chrome")
print("2 dedos: calculadora")
print("3 dedos: notas")
print("4 dedos: ChatGPT")
print("5 dedos: captura de pantalla")

with mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.5) as hands:
    while True:
        success, img = cap.read()
        if not success: break
        
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        
        dedos_levantados = 0 

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                lmList = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                if len(lmList) != 0:
                    lista_dedos = []

                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[17][1], lmList[17][2]
                    distancia_pulgar_menique = math.hypot(x2 - x1, y2 - y1)

                    x3, y3 = lmList[5][1], lmList[5][2]
                    ref_ancho_mano = math.hypot(x2 - x3, y2 - y3)

                    if distancia_pulgar_menique > ref_ancho_mano * 0.9:
                        lista_dedos.append(1)
                    else:
                        lista_dedos.append(0)

                    for id in range(0, 4):
                        if lmList[tipsIds[id]][2] < lmList[tipsIds[id]-2][2]:
                            lista_dedos.append(1)
                        else:
                            lista_dedos.append(0)

                    dedos_levantados = lista_dedos.count(1)
        
        if dedos_levantados in acciones:
            if dedos_levantados == gesto_actual:
                contador_frames += 1
                
                progreso = int((contador_frames / FRAMES_PARA_ACTIVAR) * 300)
                color_barra = (255, 0, 255) if dedos_levantados == 4 else (0, 255, 0)
                
                cv2.rectangle(img, (50, 650), (350, 680), (200, 200, 200), 2)
                cv2.rectangle(img, (50, 650), (50 + progreso, 680), color_barra, -1)
                
                nombre_accion = acciones[dedos_levantados][0]
                cv2.putText(img, f"Cargando: {nombre_accion}...", (50, 640), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_barra, 2)

                if contador_frames >= FRAMES_PARA_ACTIVAR and not accion_ejecutada:
                    comando = acciones[dedos_levantados][1]
                    if comando == "screenshot":
                        foto = pyautogui.screenshot()
                        foto.save(f"captura_{int(time.time())}.png")
                        cv2.putText(img, "foto guardada", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
                    else:
                        print(f"Abriendo {nombre_accion}")
                        os.system(comando)
                    accion_ejecutada = True 
            else:
                gesto_actual = dedos_levantados
                contador_frames = 0
                accion_ejecutada = False
        else:
            gesto_actual = 0
            contador_frames = 0
            accion_ejecutada = False

        cv2.rectangle(img, (20, 20), (150, 100), (0, 0, 0), -1)
        cv2.putText(img, f'{dedos_levantados}', (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

        cv2.imshow("Asistente de gestos - Dilan", img)
        if cv2.waitKey(1) == ord('q'): break

cap.release()
cv2.destroyAllWindows()



        