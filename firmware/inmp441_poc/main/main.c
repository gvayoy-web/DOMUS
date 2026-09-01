#include <math.h>
#include <stdint.h>

#include "driver/i2s_std.h"
#include "esp_check.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SAMPLE_RATE_HZ 16000
#define BLOCK_SAMPLES 512
#define RING_SECONDS 2
#define RING_SAMPLES (SAMPLE_RATE_HZ * RING_SECONDS)

static const char *TAG = "JARVIS_MIC";
static i2s_chan_handle_t rx_channel;
static int16_t *audio_ring;
static size_t ring_write_index;

static int16_t convertir_muestra(int32_t raw)
{
    // INMP441 entrega 24 bits significativos dentro de una ranura de 32 bits.
    // El desplazamiento deja margen para evitar saturación durante esta prueba.
    int32_t value = raw >> 14;
    if (value > INT16_MAX) value = INT16_MAX;
    if (value < INT16_MIN) value = INT16_MIN;
    return (int16_t)value;
}

static esp_err_t iniciar_inmp441(void)
{
    i2s_chan_config_t channel_cfg = I2S_CHANNEL_DEFAULT_CONFIG(
        I2S_NUM_AUTO, I2S_ROLE_MASTER);
    channel_cfg.dma_desc_num = 8;
    channel_cfg.dma_frame_num = BLOCK_SAMPLES;
    ESP_RETURN_ON_ERROR(i2s_new_channel(&channel_cfg, NULL, &rx_channel), TAG,
                        "No se pudo crear el canal I2S RX");

    i2s_std_slot_config_t slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(
        I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO);
    slot_cfg.slot_mask = CONFIG_JARVIS_MIC_RIGHT_CHANNEL
        ? I2S_STD_SLOT_RIGHT : I2S_STD_SLOT_LEFT;

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE_HZ),
        .slot_cfg = slot_cfg,
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = CONFIG_JARVIS_MIC_SCK_PIN,
            .ws = CONFIG_JARVIS_MIC_WS_PIN,
            .dout = I2S_GPIO_UNUSED,
            .din = CONFIG_JARVIS_MIC_SD_PIN,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };

    ESP_RETURN_ON_ERROR(i2s_channel_init_std_mode(rx_channel, &std_cfg), TAG,
                        "No se pudo configurar el INMP441");
    return i2s_channel_enable(rx_channel);
}

static void tarea_microfono(void *argument)
{
    (void)argument;
    int32_t *raw = heap_caps_malloc(BLOCK_SAMPLES * sizeof(int32_t),
                                    MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    if (raw == NULL) {
        ESP_LOGE(TAG, "No hay RAM interna para el bloque I2S");
        vTaskDelete(NULL);
        return;
    }

    while (true) {
        size_t bytes_read = 0;
        esp_err_t err = i2s_channel_read(rx_channel, raw,
                                         BLOCK_SAMPLES * sizeof(int32_t),
                                         &bytes_read, pdMS_TO_TICKS(1000));
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Lectura I2S falló: %s", esp_err_to_name(err));
            continue;
        }

        const size_t count = bytes_read / sizeof(int32_t);
        if (count == 0) continue;

        int64_t sum = 0;
        for (size_t i = 0; i < count; ++i) sum += convertir_muestra(raw[i]);
        const int32_t mean = (int32_t)(sum / (int64_t)count);

        uint64_t energy = 0;
        int32_t peak = 0;
        unsigned saturated = 0;
        for (size_t i = 0; i < count; ++i) {
            int32_t centered = (int32_t)convertir_muestra(raw[i]) - mean;
            int32_t absolute = centered < 0 ? -centered : centered;
            if (absolute > peak) peak = absolute;
            if (absolute >= 30000) saturated++;
            energy += (uint64_t)((int64_t)centered * centered);

            audio_ring[ring_write_index] = (int16_t)centered;
            ring_write_index = (ring_write_index + 1) % RING_SAMPLES;
        }

        const unsigned rms = (unsigned)sqrt((double)energy / (double)count);
        const bool voice_active = rms >= CONFIG_JARVIS_VAD_RMS_THRESHOLD;
        ESP_LOGI(TAG, "rms=%u peak=%ld dc=%ld voz=%s saturadas=%u/%u",
                 rms, (long)peak, (long)mean, voice_active ? "SI" : "NO",
                 saturated, (unsigned)count);
    }
}

void app_main(void)
{
    audio_ring = heap_caps_calloc(RING_SAMPLES, sizeof(int16_t),
                                  MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (audio_ring == NULL) {
        ESP_LOGE(TAG, "No se pudo reservar el búfer circular en PSRAM");
        return;
    }

    ESP_ERROR_CHECK(iniciar_inmp441());
    ESP_LOGI(TAG, "INMP441: 16 kHz, mono, búfer PSRAM de %d segundos",
             RING_SECONDS);
    xTaskCreatePinnedToCore(tarea_microfono, "jarvis_mic", 4096, NULL, 6,
                            NULL, 0);
}
