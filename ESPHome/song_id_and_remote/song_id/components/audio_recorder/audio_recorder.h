#pragma once
#include "esphome.h"
#include "esp_log.h"
#include "driver/i2s_std.h"
#include "esp_spiffs.h"
#include "esp_http_server.h"
#include "esp_partition.h"
#include "esp_heap_caps.h" 
#include <sys/unistd.h>
#include <sys/stat.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

namespace audio_recorder {

static const char *TAG = "audio_recorder";

#define SAMPLE_RATE 16000
#define WAVE_HEADER_SIZE 44

struct __attribute__((packed)) wav_header_t {
    char riff[4]; uint32_t overall_size; char wave[4]; char fmt_chunk_marker[4];
    uint32_t length_of_fmt; uint16_t format_type; uint16_t channels;
    uint32_t sample_rate; uint32_t byterate; uint16_t block_align;
    uint16_t bits_per_sample; char data_chunk_header[4]; uint32_t data_size;
};

static esp_err_t download_get_handler(httpd_req_t *req) {
    FILE *f = fopen("/spiffs/audio.wav", "rb");
    if (f == NULL) { httpd_resp_send_404(req); return ESP_FAIL; }
    httpd_resp_set_type(req, "audio/wav");
    char *chunk = (char *)malloc(1024);
    size_t chunk_size;
    while ((chunk_size = fread(chunk, 1, 1024, f)) > 0) {
        if (httpd_resp_send_chunk(req, chunk, chunk_size) != ESP_OK) {
            fclose(f); free(chunk); return ESP_FAIL;
        }
    }
    httpd_resp_send_chunk(req, NULL, 0);
    free(chunk); fclose(f);
    return ESP_OK;
}

static esp_err_t index_handler(httpd_req_t *req) {
    httpd_resp_send(req, "Mic Ready. <a href='/audio.wav'>Download</a>", HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

static const httpd_uri_t audio_uri = { .uri = "/audio.wav", .method = HTTP_GET, .handler = download_get_handler, .user_ctx = NULL };
static const httpd_uri_t root_uri = { .uri = "/", .method = HTTP_GET, .handler = index_handler, .user_ctx = NULL };

class AudioRecorder : public esphome::Component {
 public:
  int bck_pin = 0; int ws_pin = 0; int din_pin = 0;
  int gain_factor = 4;
  int duration_sec = 6;
  bool is_mounted = false;
  httpd_handle_t server = NULL; 

  // Monitoring Variables
  bool monitoring_enabled = false;
  i2s_chan_handle_t monitor_handle = NULL;
  float current_audio_level = 0.0f;
  float silence_threshold = 100.0f;
  uint32_t gap_duration_ms = 2000;
  uint32_t silence_start_time = 0;
  bool song_playing = false;
  bool gap_detected = false;
  
  TaskHandle_t recording_task_handle = NULL;
  bool recording_in_progress = false;

  void set_pins(int bck, int ws, int din) {
      this->bck_pin = bck; this->ws_pin = ws; this->din_pin = din;
  }
  void set_gain(int gain) { this->gain_factor = gain; }
  void set_duration(int duration) { this->duration_sec = duration; }

  void set_silence_threshold(float threshold) { this->silence_threshold = threshold; }
  void set_gap_duration(uint32_t duration) { this->gap_duration_ms = duration; }
  float get_audio_level() { return current_audio_level; }
  bool get_song_playing() { return song_playing; }
  bool get_gap_detected() { return gap_detected; }
  bool is_recording() { return recording_in_progress; }  // NEW:  Check if recording

  float get_setup_priority() const override { return esphome::setup_priority:: AFTER_WIFI; }

  void setup() override {
    const esp_partition_t *partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_SPIFFS, "spiffs");
    if (!partition) { ESP_LOGE(TAG, "Partition missing"); return; }

    esp_vfs_spiffs_conf_t conf = { .base_path = "/spiffs", .partition_label = "spiffs", .max_files = 5, .format_if_mount_failed = true };
    if (esp_vfs_spiffs_register(&conf) != ESP_OK) return;
    this->is_mounted = true;

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 8080; 
    config.stack_size = 8192; 
    if (httpd_start(&this->server, &config) == ESP_OK) {
        httpd_register_uri_handler(this->server, &audio_uri);
        httpd_register_uri_handler(this->server, &root_uri);
        ESP_LOGI(TAG, "Web Server started on port 8080");
    }
  }

  void start_monitoring() {
    if (monitoring_enabled) {
      ESP_LOGW(TAG, "Monitoring already running");
      return;
    }
    
    ESP_LOGI(TAG, "Starting audio level monitoring...");
    
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    if (i2s_new_channel(&chan_cfg, NULL, &this->monitor_handle) != ESP_OK) {
      ESP_LOGE(TAG, "Failed to create monitor I2S channel");
      return;
    }

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = (gpio_num_t)this->bck_pin,
            .ws = (gpio_num_t)this->ws_pin,
            .dout = I2S_GPIO_UNUSED,
            .din = (gpio_num_t)this->din_pin,
            .invert_flags = { .mclk_inv = false, .bclk_inv = false, .ws_inv = false },
        },
    };
    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_BOTH;

    if (i2s_channel_init_std_mode(this->monitor_handle, &std_cfg) != ESP_OK) {
      ESP_LOGE(TAG, "Failed to init monitor I2S channel");
      i2s_del_channel(this->monitor_handle);
      this->monitor_handle = NULL;
      return;
    }
    
    if (i2s_channel_enable(this->monitor_handle) != ESP_OK) {
      ESP_LOGE(TAG, "Failed to enable monitor I2S channel");
      i2s_del_channel(this->monitor_handle);
      this->monitor_handle = NULL;
      return;
    }
    
    monitoring_enabled = true;
    ESP_LOGI(TAG, "Monitoring started successfully");
  }

  void stop_monitoring() {
    if (!monitoring_enabled || !this->monitor_handle) return;
    
    ESP_LOGI(TAG, "Stopping audio level monitoring...");
    i2s_channel_disable(this->monitor_handle);
    i2s_del_channel(this->monitor_handle);
    this->monitor_handle = NULL;
    monitoring_enabled = false;
    current_audio_level = 0.0f;
    song_playing = false;
    gap_detected = false;
  }

  void loop() override {
    if (! monitoring_enabled || !this->monitor_handle) return;
    
    int32_t samples[128];
    size_t bytes_read = 0;
    
    if (i2s_channel_read(this->monitor_handle, samples, sizeof(samples), &bytes_read, 10) == ESP_OK) {
      float sum = 0;
      int num_samples = bytes_read / 4;
      
      for (int i = 0; i < num_samples; i++) {
        float normalized = (float)samples[i] / 65536.0f;
        sum += normalized * normalized;
      }
      
      current_audio_level = sqrt(sum / num_samples);
      
      uint32_t now = esphome::millis();
      
      if (current_audio_level >= silence_threshold) {
        if (!song_playing) {
          song_playing = true;
          ESP_LOGD(TAG, "Song playing (level: %.1f >= %.1f)", current_audio_level, silence_threshold);
        }
        gap_detected = false;
        silence_start_time = now;
        
      } else {
        if (song_playing) {
          song_playing = false;
          silence_start_time = now;
          ESP_LOGD(TAG, "Silence detected (level: %.1f < %.1f)", current_audio_level, silence_threshold);
        }
        
        if (! gap_detected && (now - silence_start_time) >= gap_duration_ms) {
          gap_detected = true;
          ESP_LOGI(TAG, "Song gap confirmed! Silence for %d ms (level: %.1f)", 
                   (now - silence_start_time), current_audio_level);
        }
      }
    }
  }

  static void recording_task_wrapper(void* param) {
    AudioRecorder* recorder = static_cast<AudioRecorder*>(param);
    recorder->recording_task_impl();
    vTaskDelete(NULL); // Task deletes itself when done
  }

  void record_audio() {
    if (!this->is_mounted) {
      ESP_LOGE(TAG, "SPIFFS not mounted");
      return;
    }
    
    if (recording_in_progress) {
      ESP_LOGW(TAG, "Recording already in progress");
      return;
    }
    
    // Stop monitoring during recording to prevent I2S conflicts
    bool was_monitoring = monitoring_enabled;
    if (was_monitoring) {
      ESP_LOGI(TAG, "Pausing monitoring for recording...");
      stop_monitoring();
    }
    
    recording_in_progress = true;
    
    xTaskCreatePinnedToCore(
        recording_task_wrapper,   // Task function
        "audio_record",           // Task name
        4096,                     // Stack size (bytes)
        this,                     // Parameter (this pointer)
        5,                        // Priority (0-24, higher = more priority)
        &recording_task_handle,   // Task handle
        0                         // Core 0 (core 1 runs Arduino/ESPHome loop)
    );
    
    ESP_LOGI(TAG, "Recording task started on separate core");
  }

  void recording_task_impl() {
    uint32_t ram_size = SAMPLE_RATE * this->duration_sec * 2 * 4;
    
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "Free PSRAM: %d. Allocating Raw Buffer: %d bytes...", free_psram, ram_size);

    uint8_t *ram_buffer = (uint8_t *)heap_caps_calloc(1, ram_size, MALLOC_CAP_SPIRAM);
    if (ram_buffer == NULL) { 
      ESP_LOGE(TAG, "Not enough PSRAM!");
      recording_in_progress = false;
      return; 
    }

    ESP_LOGI(TAG, "Starting 32-bit Native Capture...");

    i2s_chan_handle_t rx_handle = NULL;
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    
    if (i2s_new_channel(&chan_cfg, NULL, &rx_handle) != ESP_OK) {
      ESP_LOGE(TAG, "Failed to create I2S channel");
      free(ram_buffer);
      recording_in_progress = false;
      return;
    }

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = (gpio_num_t)this->bck_pin,
            .ws = (gpio_num_t)this->ws_pin,
            .dout = I2S_GPIO_UNUSED,
            .din = (gpio_num_t)this->din_pin,
            .invert_flags = { .mclk_inv = false, .bclk_inv = false, .ws_inv = false },
        },
    };
    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_BOTH; 

    if (i2s_channel_init_std_mode(rx_handle, &std_cfg) != ESP_OK ||
        i2s_channel_enable(rx_handle) != ESP_OK) {
      ESP_LOGE(TAG, "Failed to initialize I2S");
      i2s_del_channel(rx_handle);
      free(ram_buffer);
      recording_in_progress = false;
      return;
    }

    size_t chunk_size = 1024; 
    size_t bytes_read = 0;
    int ram_offset = 0;
    char *dma_buf = (char *)calloc(chunk_size, 1);
    uint32_t start_ms = esphome::millis();

    while (ram_offset < ram_size) {
        if (i2s_channel_read(rx_handle, dma_buf, chunk_size, &bytes_read, 1000) == ESP_OK) {
            memcpy(ram_buffer + ram_offset, dma_buf, bytes_read);
            ram_offset += bytes_read;
        }
        vTaskDelay(1); // Yield to other tasks (including WiFi, remote control, etc.)
    }
    
    // Stop I2S
    i2s_channel_disable(rx_handle);
    i2s_del_channel(rx_handle);
    free(dma_buf);

    uint32_t duration_ms = esphome::millis() - start_ms;
    ESP_LOGI(TAG, "Captured in %d ms. Processing & Saving...", duration_ms);

    unlink("/spiffs/audio.wav");
    FILE *f = fopen("/spiffs/audio.wav", "wb");
    if (f == NULL) { 
        ESP_LOGE(TAG, "Failed to open file"); 
        free(ram_buffer);
        recording_in_progress = false;
        return; 
    }

    uint32_t final_size = ram_size / 4; 
    write_wav_header(f, final_size);

    int32_t *input_32 = (int32_t *)ram_buffer;
    int total_samples = ram_size / 4;
    int16_t *output_16 = (int16_t *)malloc(1024);
    int out_idx = 0;
    int max_val = 0;

    for (int i = 0; i < total_samples; i += 2) {
        int32_t left = input_32[i];
        int32_t right = input_32[i+1];
        int32_t mixed = (left + right) / 2;
        int32_t val = (mixed >> 14) * this->gain_factor;

        if (val > 32767) val = 32767;
        if (val < -32768) val = -32768;
        
        if (abs(val) > max_val) max_val = abs(val);
        output_16[out_idx++] = (int16_t)val;

        if (out_idx >= 512) {
            fwrite(output_16, 2, 512, f);
            out_idx = 0;
            vTaskDelay(1); // Yield during file writing
        }
    }
    
    if (out_idx > 0) fwrite(output_16, 2, out_idx, f);

    fclose(f);
    free(ram_buffer);
    free(output_16);

    ESP_LOGI(TAG, "File Saved. Peak Volume: %d", max_val);
    
    recording_in_progress = false;
    
    ESP_LOGI(TAG, "Recording complete");
  }

 private:
  void write_wav_header(FILE *f, int dataSize) {
      wav_header_t header;
      memcpy(header.riff, "RIFF", 4);
      header.overall_size = dataSize + sizeof(wav_header_t) - 8;
      memcpy(header.wave, "WAVE", 4);
      memcpy(header.fmt_chunk_marker, "fmt ", 4);
      header.length_of_fmt = 16; header.format_type = 1; header.channels = 1;
      header.sample_rate = SAMPLE_RATE; 
      header.bits_per_sample = 16;
      header.byterate = SAMPLE_RATE * 1 * 16 / 8; 
      header.block_align = 1 * 16 / 8;
      memcpy(header.data_chunk_header, "data", 4);
      header.data_size = dataSize;
      fwrite(&header, sizeof(wav_header_t), 1, f);
  }
};

}
