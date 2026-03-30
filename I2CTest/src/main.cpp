#include <Arduino.h>
#include <Wire.h>

static const uint8_t ADDR_LOW  = 119; // 0x77 — reads 8 pads
static const uint8_t ADDR_HIGH = 120; // 0x78 — reads 12 pads
static const uint16_t CAPACITIVE_THRESHOLD = 0; // TODO: set after observing dry/wet raw values

void setup() {
    Serial.begin(9600);
    Wire.begin();
}

void loop() {
    uint16_t readings[20] = {0};

    // Read 8 pads from low address (2 bytes each, little-endian)
    uint8_t buf_low[16] = {0};
    Wire.requestFrom(ADDR_LOW, (uint8_t)16);
    for (uint8_t i = 0; i < 16 && Wire.available(); i++) {
        buf_low[i] = Wire.read();
    }
    for (uint8_t i = 0; i < 8; i++) {
        readings[i] = (uint16_t)buf_low[i * 2] | ((uint16_t)buf_low[i * 2 + 1] << 8);
    }

    // Read 12 pads from high address (2 bytes each, little-endian)
    uint8_t buf_high[24] = {0};
    Wire.requestFrom(ADDR_HIGH, (uint8_t)24);
    for (uint8_t i = 0; i < 24 && Wire.available(); i++) {
        buf_high[i] = Wire.read();
    }
    for (uint8_t i = 0; i < 12; i++) {
        readings[8 + i] = (uint16_t)buf_high[i * 2] | ((uint16_t)buf_high[i * 2 + 1] << 8);
    }

    // Count submerged pads
    uint8_t submerged = 0;
    for (uint8_t i = 0; i < 20; i++) {
        if (readings[i] >= CAPACITIVE_THRESHOLD) {
            submerged++;
        }
    }

    float percent = (submerged / 20.0f) * 100.0f;

    // Print raw pad values
    Serial.print("WLS: [");
    for (uint8_t i = 0; i < 20; i++) {
        Serial.print(readings[i]);
        if (i < 19) Serial.print(", ");
    }
    Serial.print("] — ");

    // Print percentage
    Serial.print(percent, 1);
    Serial.println("%");

    delay(1000);
}
