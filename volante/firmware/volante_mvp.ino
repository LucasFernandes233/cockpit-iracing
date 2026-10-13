/*
  Volante de simulação — firmware do MVP (rev00)
  Placa: Raspberry Pi Pico (RP2040), core "arduino-pico" (Earle Philhower)
  Ferramentas > USB Stack: "Pico SDK"  (a biblioteca Joystick usa o USB nativo)

  O volante aparece no Windows como um joystick USB comum (HID), sem driver.
  iRacing e demais simuladores enxergam apenas botões numerados de 1 a 22:

    Botões  1–12  B1..B12  matriz 4 linhas × 3 colunas, com diodos
    Botões 13–20  encoders E1..E4 (cada clique vira um toque curto)
                  E1: 13 horário / 14 anti-horário    E2: 15 / 16
                  E3: 17 / 18                         E4: 19 / 20
    Botão  21     aleta esquerda (descer marcha)  — sensor Hall
    Botão  22     aleta direita  (subir marcha)   — sensor Hall

  Ligações (ver tabela de pinagem no documento do projeto):
    Linhas da matriz : GP2, GP3, GP4, GP5   (saída, uma por vez em nível baixo)
    Colunas da matriz: GP6, GP7, GP8        (entrada com pull-up interno)
    Diodo 1N4148 em série com cada botão, faixa (catodo) voltada para a LINHA.
    Encoders (A, B)  : E1 GP10/GP11, E2 GP12/GP13, E3 GP14/GP15, E4 GP16/GP17
                       pino central (C) do encoder no GND
    Hall SS49E       : saída da aleta esq. no GP26 (ADC0), dir. no GP27 (ADC1)
                       alimentação no 3V3(OUT), GND no AGND
*/

#include <Joystick.h>

// ------------------------------------------------------------------ pinos
const uint8_t N_ROWS = 4;
const uint8_t N_COLS = 3;
const uint8_t ROW_PINS[N_ROWS] = {2, 3, 4, 5};
const uint8_t COL_PINS[N_COLS] = {6, 7, 8};

const uint8_t N_ENC = 4;
const uint8_t ENC_PINS[N_ENC][2] = {{10, 11}, {12, 13}, {14, 15}, {16, 17}};

const uint8_t N_PADDLES = 2;
const uint8_t HALL_PINS[N_PADDLES] = {26, 27};  // esquerda, direita

// ------------------------------------------------------ mapa de botões HID
const uint8_t BTN_ENC_BASE = 13;                       // 13..20
const uint8_t PADDLE_BTN[N_PADDLES] = {21, 22};        // esq., dir.
const uint8_t N_BUTTONS = 22;

// --------------------------------------------------------------- ajustes
const uint32_t DEBOUNCE_MS      = 5;     // requisito VOL-FW-03
const uint32_t SCAN_INTERVAL_US = 1000;  // varredura da matriz a 1 kHz
const uint32_t ENC_PULSE_ON_MS  = 40;    // tempo "apertado" por clique de encoder
const uint32_t ENC_PULSE_OFF_MS = 20;    // intervalo entre cliques seguidos
const int16_t  ENC_MAX_PENDING  = 8;     // cliques acumulados no máximo
const bool     ENC_INVERT[N_ENC] = {false, false, false, false};  // inverte sentido

const int      HALL_MIN_SPAN    = 150;   // curso mínimo (contagens ADC) para valer
const float    HALL_PRESS       = 0.60;  // aciona a 60% do curso
const float    HALL_RELEASE     = 0.40;  // solta abaixo de 40% (histerese)

const bool     DEBUG_SERIAL     = false; // true = imprime leituras no monitor serial

// ---------------------------------------------------------------- estado
bool btnState[N_BUTTONS + 1];   // índice 1..22 (0 não usado)
bool sentState[N_BUTTONS + 1];

struct Key {
  bool stable = false;
  bool last = false;
  uint32_t changedAt = 0;
};
Key keys[N_ROWS * N_COLS];

struct Encoder {
  uint8_t prev = 3;
  int8_t acc = 0;
  int16_t pending = 0;
  bool on = false;
  uint32_t t = 0;
};
Encoder enc[N_ENC];

struct Paddle {
  int rest = 0;
  int maxTravel = 0;
  bool pressed = false;
  int raw = 0;
};
Paddle paddles[N_PADDLES];

// Tabela de decodificação em quadratura: índice = (estado anterior << 2) | atual
const int8_t QDEC[16] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};

uint32_t lastScanUs = 0;
uint32_t lastSendMs = 0;
uint32_t lastDebugMs = 0;

// ------------------------------------------------------------- matriz
void scanMatrix(uint32_t now) {
  for (uint8_t r = 0; r < N_ROWS; r++) {
    pinMode(ROW_PINS[r], OUTPUT);
    digitalWrite(ROW_PINS[r], LOW);
    delayMicroseconds(10);  // tempo para o sinal assentar

    for (uint8_t c = 0; c < N_COLS; c++) {
      uint8_t idx = r * N_COLS + c;
      bool raw = (digitalRead(COL_PINS[c]) == LOW);
      Key &k = keys[idx];
      if (raw != k.last) {
        k.last = raw;
        k.changedAt = now;
      } else if (raw != k.stable && (now - k.changedAt) >= DEBOUNCE_MS) {
        k.stable = raw;
      }
      btnState[1 + idx] = k.stable;
    }
    pinMode(ROW_PINS[r], INPUT);  // linha volta a alta impedância
  }
}

// ----------------------------------------------------------- encoders
void readEncoders() {
  for (uint8_t i = 0; i < N_ENC; i++) {
    Encoder &e = enc[i];
    uint8_t s = (digitalRead(ENC_PINS[i][0]) << 1) | digitalRead(ENC_PINS[i][1]);
    if (s == e.prev) continue;
    e.acc += QDEC[(e.prev << 2) | s];
    e.prev = s;

    // EC11 comum: 1 ciclo completo por clique, repouso em 11 (com pull-up)
    if (s == 3) {
      int8_t dir = 0;
      if (e.acc >= 2) dir = 1;
      else if (e.acc <= -2) dir = -1;
      if (ENC_INVERT[i]) dir = -dir;
      int16_t p = e.pending + dir;
      if (p > ENC_MAX_PENDING) p = ENC_MAX_PENDING;
      if (p < -ENC_MAX_PENDING) p = -ENC_MAX_PENDING;
      e.pending = p;
      e.acc = 0;
    }
  }
}

void updateEncoderPulses(uint32_t now) {
  for (uint8_t i = 0; i < N_ENC; i++) {
    Encoder &e = enc[i];
    uint8_t bCW = BTN_ENC_BASE + 2 * i;
    uint8_t bCCW = bCW + 1;

    if (e.on) {
      if (now - e.t >= ENC_PULSE_ON_MS) {
        btnState[bCW] = false;
        btnState[bCCW] = false;
        e.on = false;
        e.t = now;
      }
    } else if (e.pending != 0 && (now - e.t) >= ENC_PULSE_OFF_MS) {
      bool cw = e.pending > 0;
      btnState[cw ? bCW : bCCW] = true;
      e.pending += cw ? -1 : 1;
      e.on = true;
      e.t = now;
    }
  }
}

// ------------------------------------------------------------- aletas
int readAveraged(uint8_t pin, uint8_t n) {
  long sum = 0;
  for (uint8_t i = 0; i < n; i++) sum += analogRead(pin);
  return sum / n;
}

void calibratePaddlesAtRest() {
  // Aletas soltas durante a inicialização: guarda o valor de repouso
  for (uint8_t i = 0; i < N_PADDLES; i++) {
    paddles[i].rest = readAveraged(HALL_PINS[i], 64);
    paddles[i].maxTravel = 0;
  }
}

void readPaddles() {
  for (uint8_t i = 0; i < N_PADDLES; i++) {
    Paddle &p = paddles[i];
    p.raw = readAveraged(HALL_PINS[i], 4);
    int travel = abs(p.raw - p.rest);         // vale para qualquer polo do ímã
    if (travel > p.maxTravel) p.maxTravel = travel;  // autocalibração do curso

    if (p.maxTravel >= HALL_MIN_SPAN) {
      float f = (float)travel / p.maxTravel;
      if (!p.pressed && f >= HALL_PRESS) p.pressed = true;
      else if (p.pressed && f <= HALL_RELEASE) p.pressed = false;
    }
    btnState[PADDLE_BTN[i]] = p.pressed;
  }
}

// --------------------------------------------------------------- envio
void sendIfChanged(uint32_t now) {
  if (now - lastSendMs < 1) return;  // no máximo 1 relatório por ms
  bool changed = false;
  for (uint8_t b = 1; b <= N_BUTTONS; b++) {
    if (btnState[b] != sentState[b]) {
      Joystick.button(b, btnState[b]);
      sentState[b] = btnState[b];
      changed = true;
    }
  }
  if (changed) {
    Joystick.send_now();
    lastSendMs = now;
  }
}

void debugPrint(uint32_t now) {
  if (!DEBUG_SERIAL || now - lastDebugMs < 200) return;
  lastDebugMs = now;
  Serial.print("botoes: ");
  for (uint8_t b = 1; b <= N_BUTTONS; b++) Serial.print(btnState[b] ? '1' : '0');
  for (uint8_t i = 0; i < N_PADDLES; i++) {
    Serial.printf("  aleta%u raw=%d repouso=%d curso=%d", i, paddles[i].raw,
                  paddles[i].rest, paddles[i].maxTravel);
  }
  Serial.println();
}

// ----------------------------------------------------------- setup/loop
void setup() {
  for (uint8_t r = 0; r < N_ROWS; r++) pinMode(ROW_PINS[r], INPUT);
  for (uint8_t c = 0; c < N_COLS; c++) pinMode(COL_PINS[c], INPUT_PULLUP);
  for (uint8_t i = 0; i < N_ENC; i++) {
    pinMode(ENC_PINS[i][0], INPUT_PULLUP);
    pinMode(ENC_PINS[i][1], INPUT_PULLUP);
  }
  analogReadResolution(12);
  delay(50);
  for (uint8_t i = 0; i < N_ENC; i++) {
    enc[i].prev = (digitalRead(ENC_PINS[i][0]) << 1) | digitalRead(ENC_PINS[i][1]);
  }
  calibratePaddlesAtRest();

  if (DEBUG_SERIAL) Serial.begin(115200);
  Joystick.useManualSend(true);
  Joystick.begin();
}

void loop() {
  uint32_t nowMs = millis();
  uint32_t nowUs = micros();

  readEncoders();  // a cada volta do loop: não perde passos em giro rápido

  if (nowUs - lastScanUs >= SCAN_INTERVAL_US) {
    lastScanUs = nowUs;
    scanMatrix(nowMs);
    readPaddles();
  }

  updateEncoderPulses(nowMs);
  sendIfChanged(nowMs);
  debugPrint(nowMs);
}
