#include <stddef.h>
#include <string.h>

#include "driver/i2s_std.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "picotts.h"

static const char *TAG = "JARVIS_TTS";
static i2s_chan_handle_t tx_channel;

static void escribir_audio(int16_t *samples, unsigned count)
{
    size_t bytes_written = 0;
    const size_t bytes = count * sizeof(int16_t);
    esp_err_t err = i2s_channel_write(tx_channel, samples, bytes,
                                      &bytes_written, portMAX_DELAY);
    if (err != ESP_OK || bytes_written != bytes) {
        ESP_LOGE(TAG, "Fallo I2S: %s, %u/%u bytes",
                 esp_err_to_name(err), (unsigned)bytes_written, (unsigned)bytes);
    }
}

static void tts_finalizado(void)
{
    ESP_LOGI(TAG, "Frase terminada; aquí se reactivará el micrófono");
}

static void tts_error(void)
{
    ESP_LOGE(TAG, "PicoTTS informó un error");
}

static esp_err_t iniciar_max98357a(void)
{
    i2s_chan_config_t channel_cfg = I2S_CHANNEL_DEFAULT_CONFIG(
        I2S_NUM_AUTO, I2S_ROLE_MASTER);
    ESP_RETURN_ON_ERROR(i2s_new_channel(&channel_cfg, &tx_channel, NULL), TAG,
                        "No se pudo crear el canal I2S");

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(PICOTTS_SAMPLE_FREQ_HZ),
        .slot_cfg = I2S_STD_MSB_SLOT_DEFAULT_CONFIG(
            I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = CONFIG_JARVIS_I2S_BCLK_PIN,
            .ws = CONFIG_JARVIS_I2S_WS_PIN,
            .dout = CONFIG_JARVIS_I2S_DOUT_PIN,
            .din = I2S_GPIO_UNUSED,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };

    ESP_RETURN_ON_ERROR(i2s_channel_init_std_mode(tx_channel, &std_cfg), TAG,
                        "No se pudo configurar I2S");
    return i2s_channel_enable(tx_channel);
}

void app_main(void)
{
    ESP_ERROR_CHECK(iniciar_max98357a());

    if (!picotts_init(5, escribir_audio, 1)) {
        ESP_LOGE(TAG, "No se pudo iniciar PicoTTS; comprueba PSRAM y recursos es-ES");
        return;
    }

    picotts_set_idle_notify(tts_finalizado);
    picotts_set_error_notify(tts_error);

    static const char saludo[] =
        "Hola, soy Jarvis. El sistema de voz local está funcionando.";
    ESP_LOGI(TAG, "Enviando frase española a PicoTTS");
    picotts_add(saludo, sizeof(saludo));
}
