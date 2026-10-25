"""
Monitor de atenção: usa a webcam para detectar
  1) olhos fechados por muito tempo (sonolência)
  2) cabeça/olhar desviado do foco por muito tempo
e toca um alerta sonoro.

Instalação (Python 3.9 a 3.12):
    pip install opencv-python mediapipe numpy

Uso:
    python monitor_atencao.py
Teclas:  c = recalibrar   q = sair
Ao iniciar, olhe para a tela (seu "foco") por ~3 segundos: é a calibração.
"""

import os
import platform
import threading
import time

import cv2
import mediapipe as mp
import numpy as np

# ----------------------- CONFIGURAÇÕES (ajuste aqui) -----------------------
CAMERA_INDEX = 0            # 0 = webcam padrão
CALIB_SECONDS = 3.0         # tempo de calibração
EYES_CLOSED_SECONDS = 1.5   # olhos fechados por mais que isso => alerta
LOOK_AWAY_SECONDS = 2.5     # desvio de foco por mais que isso => alerta
NO_FACE_SECONDS = 3.0       # rosto ausente por mais que isso => alerta
EAR_FACTOR = 0.75           # olho "fechado" = EAR abaixo de 75% do normal
GAZE_TOLERANCE = 0.12       # tolerância do olhar (íris) horizontal
HEAD_TOLERANCE = 0.12       # tolerância de giro/inclinação da cabeça
ALERT_INTERVAL = 2.0        # segundos entre repetições do alarme
# ---------------------------------------------------------------------------

# Índices dos pontos do MediaPipe Face Mesh
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]
NOSE, CHEEK_L, CHEEK_R, FOREHEAD, CHIN = 1, 234, 454, 10, 152
IRIS_R, IRIS_L = 468, 473  # exigem refine_landmarks=True


def dist(a, b):
    return float(np.linalg.norm(a - b))


def eye_aspect_ratio(pts, idx):
    p = [pts[i] for i in idx]
    return (dist(p[1], p[5]) + dist(p[2], p[4])) / (2.0 * dist(p[0], p[3]) + 1e-6)


def iris_ratio(pts, iris, corner_a, corner_b):
    """Posição horizontal da íris entre os dois cantos do olho (0..1)."""
    xa, xb = pts[corner_a][0], pts[corner_b][0]
    return (pts[iris][0] - xa) / (xb - xa + 1e-6)


def extract_features(pts):
    ear = (eye_aspect_ratio(pts, LEFT_EYE) + eye_aspect_ratio(pts, RIGHT_EYE)) / 2
    iris = (iris_ratio(pts, IRIS_R, 33, 133) + iris_ratio(pts, IRIS_L, 362, 263)) / 2
    yaw = (pts[NOSE][0] - pts[CHEEK_L][0]) / (pts[CHEEK_R][0] - pts[CHEEK_L][0] + 1e-6)
    pitch = (pts[NOSE][1] - pts[FOREHEAD][1]) / (pts[CHIN][1] - pts[FOREHEAD][1] + 1e-6)
    return np.array([ear, iris, yaw, pitch])


# ------------------------------- ALARME -----------------------------------
_last_alarm = 0.0


def _beep():
    system = platform.system()
    if system == "Windows":
        import winsound
        winsound.Beep(1000, 500)
    elif system == "Darwin":
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")
    else:
        # Linux: tenta paplay; senão, sino do terminal
        if os.system("paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga 2>/dev/null") != 0:
            print("\a", end="", flush=True)


def alarm():
    global _last_alarm
    now = time.time()
    if now - _last_alarm >= ALERT_INTERVAL:
        _last_alarm = now
        threading.Thread(target=_beep, daemon=True).start()


# -------------------------------- MAIN ------------------------------------
def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit("Não consegui abrir a câmera. Verifique CAMERA_INDEX e as permissões.")

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    calib_start = time.time()
    calib_samples = []
    baseline = None

    eyes_closed_since = None
    away_since = None
    last_face_seen = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        result = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        status, color, alert = "OK", (0, 200, 0), False
        now = time.time()

        if result.multi_face_landmarks:
            last_face_seen = now
            lm = result.multi_face_landmarks[0].landmark
            pts = np.array([[p.x * w, p.y * h] for p in lm])
            feat = extract_features(pts)

            if baseline is None:
                # ---- calibração ----
                calib_samples.append(feat)
                left = max(0.0, CALIB_SECONDS - (now - calib_start))
                status, color = f"Calibrando... olhe para o foco ({left:.1f}s)", (0, 200, 255)
                if now - calib_start >= CALIB_SECONDS and len(calib_samples) > 10:
                    baseline = np.median(np.array(calib_samples), axis=0)
            else:
                ear, iris, yaw, pitch = feat
                b_ear, b_iris, b_yaw, b_pitch = baseline

                # ---- olhos fechados ----
                if ear < b_ear * EAR_FACTOR:
                    eyes_closed_since = eyes_closed_since or now
                else:
                    eyes_closed_since = None

                # ---- desvio de foco (cabeça ou olhar) ----
                looking_away = (
                    abs(yaw - b_yaw) > HEAD_TOLERANCE
                    or abs(pitch - b_pitch) > HEAD_TOLERANCE
                    or (eyes_closed_since is None and abs(iris - b_iris) > GAZE_TOLERANCE)
                )
                if looking_away:
                    away_since = away_since or now
                else:
                    away_since = None

                if eyes_closed_since and now - eyes_closed_since > EYES_CLOSED_SECONDS:
                    status, color, alert = "ALERTA: SONOLENCIA!", (0, 0, 255), True
                elif away_since and now - away_since > LOOK_AWAY_SECONDS:
                    status, color, alert = "ALERTA: FOCO DESVIADO!", (0, 0, 255), True

                cv2.putText(frame, f"EAR {ear:.2f} (base {b_ear:.2f})", (10, h - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, f"olhar {iris:.2f}  yaw {yaw:.2f}  pitch {pitch:.2f}",
                            (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            if baseline is not None and now - last_face_seen > NO_FACE_SECONDS:
                status, color, alert = "ALERTA: ROSTO NAO DETECTADO", (0, 0, 255), True
            elif baseline is None:
                calib_start = now  # só conta a calibração com rosto visível

        if alert:
            alarm()
            cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 8)

        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.imshow("Monitor de atencao (q = sair, c = recalibrar)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("c"):
            baseline, calib_samples, calib_start = None, [], time.time()
            eyes_closed_since = away_since = None

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()