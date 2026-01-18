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
#include <math.h>

namespace audio_recorder {

static const char *TAG = "audio_recorder";

#define SAMPLE_RATE 16000
#define MONITOR_BUFFER_SIZE 512 

struct __attribute__((packed)) wav_header_t {
    char riff[4]; uint32_t overall_size; char wave[4]; char fmt_chunk_marker[4];
    uint32_t length_of_fmt; uint16_t format_type; uint16_t channels;
    uint32_t sample_rate; uint32_t byterate; uint16_t block_align;
    uint16_t bits_per_sample; char data_chunk_header[4]; uint32_t data_size;
};

// Context for the background save task
struct SaveContext {
    uint8_t *buffer;
    uint32_t ram_size;
    int gain_factor;
    void *recorder_instance;
};

// --- WEB SERVER HANDLERS ---
static esp_err_t download_get_handler(httpd_req_t *req) {
    FILE *f = fopen("/spiffs/audio.wav", "rb");
    if (f == NULL) { httpd_resp_send_404(req); return ESP_FAIL; }
    httpd_resp_set_type(req, "audio/wav");
    char *chunk = (char *)malloc(4096); // Increased buffer for faster download
    size_t chunk_size;
    while ((chunk_size = fread(chunk, 1, 4096, f)) > 0) {
        if (httpd_resp_send_chunk(req, chunk, chunk_size) != ESP_OK) {
            fclose(f); free(chunk); return ESP_FAIL;
        }
    }
    httpd_resp_send_chunk(req, NULL, 0);
    free(chunk); fclose(f);
    return ESP_OK;
}

static esp_err_t index_handler(httpd_req_t *req) {
    httpd_resp_send(req, "Mic Ready. <a href='/audio.wav'>Download Latest Recording</a>", HTTPD_RESP_USE_STRLEN);
    return ESP_OK;
}

static const httpd_uri_t audio_uri = { .uri = "/audio.wav", .method = HTTP_GET, .handler = download_get_handler, .user_ctx = NULL };
static const httpd_uri_t root_uri = { .uri = "/", .method = HTTP_GET, .handler = index_handler, .user_ctx = NULL };

class AudioRecorder : public esphome::Component {
 public:
  int bck_pin = 0; int ws_pin = 0; int din_pin = 0;
  int gain_factor = 4;
  int duration_sec = 10;
  bool is_mounted = false;
  httpd_handle_t server = NULL; 

  // --- Monitoring & State ---
  bool monitoring_enabled = false;
  i2s_chan_handle_t monitor_handle = NULL;
  
  float current_rms = 0.0f;
  float current_variance = 0.0f; 
  
  float window_min_rms = 100000.0f;
  float window_max_rms = 0.0f;
  uint32_t window_start_time = 0;
  uint32_t last_log_time = 0;
  
  // --- Recording State ---
  TaskHandle_t recording_task_handle = NULL;
  
  // Flags used to coordinate tasks
  volatile bool recording_in_progress = false; // True only during capture
  volatile bool is_saving = false;             // True during background save
  bool should_resume_monitoring = false;

  void set_pins(int bck, int ws, int din) {
      this->bck_pin = bck; this->ws_pin = ws; this->din_pin = din;
  }
  void set_gain(int gain) { this->gain_factor = gain; }
  void set_duration(int duration) { this->duration_sec = duration; }

  // Dummy setters for yaml compatibility
  void set_silence_threshold(float threshold) { } 
  void set_gap_duration(uint32_t duration) { }
  
  float get_audio_level() { return current_rms; }
  float get_variance() { return current_variance; }
  
  // Exposed state: Recording OR Saving
  bool is_recording() { return recording_in_progress || is_saving; }

  float get_setup_priority() const override { return esphome::setup_priority::AFTER_WIFI; }

  void setup() override {
    const esp_partition_t *partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_SPIFFS, "spiffs");
    if (partition) {
        esp_vfs_spiffs_conf_t conf = { .base_path = "/spiffs", .partition_label = "spiffs", .max_files = 5, .format_if_mount_failed = true };
        esp_vfs_spiffs_register(&conf);
        this->is_mounted = true;
    } else {
        ESP_LOGE(TAG, "SPIFFS Partition NOT FOUND");
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 8080; 
    config.stack_size = 8192; 
    if (httpd_start(&this->server, &config) == ESP_OK) {
        httpd_register_uri_handler(this->server, &audio_uri);
        httpd_register_uri_handler(this->server, &root_uri);
        ESP_LOGI(TAG, "Web Server started");
    }
  }

  // --- PASSIVE MONITORING ---
  void start_monitoring() {
    if (monitoring_enabled || recording_in_progress) return;
    
    ESP_LOGI(TAG, "Starting Passive Monitoring...");
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    if (i2s_new_channel(&chan_cfg, NULL, &this->monitor_handle) != ESP_OK) return;

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)this->bck_pin, .ws = (gpio_num_t)this->ws_pin,
            .dout = I2S_GPIO_UNUSED, .din = (gpio_num_t)this->din_pin,
            .invert_flags = {0,0,0},
        },
    };
    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_BOTH;
    if (i2s_channel_init_std_mode(this->monitor_handle, &std_cfg) == ESP_OK) {
        i2s_channel_enable(this->monitor_handle);
        monitoring_enabled = true;
        // Reset Logic
        window_start_time = esphome::millis();
        window_min_rms = 100000.0f; window_max_rms = 0.0f;
    }
  }

  void stop_monitoring() {
    if (!monitoring_enabled || !this->monitor_handle) return;
    i2s_channel_disable(this->monitor_handle);
    i2s_del_channel(this->monitor_handle);
    this->monitor_handle = NULL;
    monitoring_enabled = false;
  }

  void loop() override {
    // Resume monitoring ASAP after capture finishes (even if saving is still happening)
    if (should_resume_monitoring && !recording_in_progress) {
      should_resume_monitoring = false;
      start_monitoring();
    }

    if (!monitoring_enabled || !this->monitor_handle || recording_in_progress) return;
    
    int32_t samples[MONITOR_BUFFER_SIZE];
    size_t bytes_read = 0;
    if (i2s_channel_read(this->monitor_handle, samples, sizeof(samples), &bytes_read, 0) == ESP_OK) {
      process_audio_chunk((char*)samples, bytes_read);
    }
  }

  // --- BACKGROUND SAVE TASK ---
  static void save_task_wrapper(void* param) {
      SaveContext *ctx = (SaveContext*)param;
      AudioRecorder *recorder = (AudioRecorder*)ctx->recorder_instance;
      recorder->save_task_impl(ctx);
      vTaskDelete(NULL);
  }

  void save_task_impl(SaveContext *ctx) {
      this->is_saving = true;
      ESP_LOGI(TAG, "Background Saving Started...");

      unlink("/spiffs/audio.wav"); 
      FILE *f = fopen("/spiffs/audio.wav", "wb");
      if (f) {
          wav_header_t header; 
          int dataSize = ctx->ram_size / 4; 
          
          memcpy(header.riff, "RIFF", 4); header.overall_size = dataSize + 36;
          memcpy(header.wave, "WAVE", 4); memcpy(header.fmt_chunk_marker, "fmt ", 4);
          header.length_of_fmt = 16; header.format_type = 1; header.channels = 1;
          header.sample_rate = SAMPLE_RATE; header.bits_per_sample = 16;
          header.byterate = SAMPLE_RATE * 2; header.block_align = 2;
          memcpy(header.data_chunk_header, "data", 4); header.data_size = dataSize;
          fwrite(&header, sizeof(wav_header_t), 1, f);

          int32_t *input_32 = (int32_t *)ctx->buffer;
          // Increased write buffer to 4KB for faster SPIFFS write
          const int WRITE_BUF_SIZE = 2048; 
          int16_t *output_16 = (int16_t *)malloc(WRITE_BUF_SIZE * sizeof(int16_t));
          int out_idx = 0;
          
          for (int i = 0; i < (ctx->ram_size/4); i += 2) {
              int32_t val = ((input_32[i] + input_32[i+1]) / 2 >> 14) * ctx->gain_factor;
              if (val > 32767) val = 32767; if (val < -32768) val = -32768;
              output_16[out_idx++] = (int16_t)val;
              
              if (out_idx >= WRITE_BUF_SIZE) {
                  fwrite(output_16, 2, WRITE_BUF_SIZE, f);
                  out_idx = 0;
                  // Yield to allow other tasks (like Monitoring!) to run
                  vTaskDelay(1); 
              }
          }
          if (out_idx > 0) fwrite(output_16, 2, out_idx, f);
          
          fclose(f); 
          free(output_16);
      } else {
          ESP_LOGE(TAG, "Failed to open file for saving");
      }

      free(ctx->buffer);
      free(ctx);
      this->is_saving = false;
      ESP_LOGI(TAG, "Background Saving Finished.");
  }

  // --- CAPTURE TASK ---
  static void recording_task_wrapper(void* param) {
    AudioRecorder* recorder = static_cast<AudioRecorder*>(param);
    recorder->recording_task_impl();
    vTaskDelete(NULL);
  }

  void record_audio() {
    if (!this->is_mounted) return;
    
    // Prevent OOM: Cannot record if we are still flushing the previous file
    if (is_saving) {
        ESP_LOGW(TAG, "Cannot record: Still saving previous file.");
        return;
    }
    if (recording_in_progress) return;
    
    if (monitoring_enabled) { should_resume_monitoring = true; stop_monitoring(); }
    
    recording_in_progress = true;
    xTaskCreatePinnedToCore(recording_task_wrapper, "audio_capture", 4096, this, 10, &recording_task_handle, 0); // High priority capture
  }

  void recording_task_impl() {
    uint32_t ram_size = SAMPLE_RATE * this->duration_sec * 2 * 4;
    ESP_LOGI(TAG, "Starting Capture. Allocating %d bytes...", ram_size);
    
    uint8_t *ram_buffer = (uint8_t *)heap_caps_calloc(1, ram_size, MALLOC_CAP_SPIRAM);
    if (!ram_buffer) { 
      ESP_LOGE(TAG, "OOM: Failed to allocate PSRAM");
      recording_in_progress = false; should_resume_monitoring = true;
      return; 
    }

    i2s_chan_handle_t rx_handle = NULL;
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    i2s_new_channel(&chan_cfg, NULL, &rx_handle);
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED, .bclk = (gpio_num_t)this->bck_pin, .ws = (gpio_num_t)this->ws_pin,
            .dout = I2S_GPIO_UNUSED, .din = (gpio_num_t)this->din_pin,
            .invert_flags = {0,0,0},
        },
    };
    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_BOTH; 
    i2s_channel_init_std_mode(rx_handle, &std_cfg);
    i2s_channel_enable(rx_handle);

    size_t chunk_size = 1024; size_t bytes_read = 0; int ram_offset = 0;
    char *dma_buf = (char *)calloc(chunk_size, 1);
    
    // Reset Live Analysis
    this->window_min_rms = 100000.0f; this->window_max_rms = 0.0f;
    this->window_start_time = esphome::millis();

    while (ram_offset < ram_size) {
        if (i2s_channel_read(rx_handle, dma_buf, chunk_size, &bytes_read, 1000) == ESP_OK) {
            memcpy(ram_buffer + ram_offset, dma_buf, bytes_read);
            ram_offset += bytes_read;
            process_audio_chunk(dma_buf, bytes_read); // Live updates
        }
        vTaskDelay(1);
    }
    
    // Shutdown I2S
    i2s_channel_disable(rx_handle); i2s_del_channel(rx_handle); free(dma_buf);

    ESP_LOGI(TAG, "Capture Complete. Offloading to Background Save...");

    // Prepare Context for Save Task
    SaveContext *ctx = (SaveContext*)malloc(sizeof(SaveContext));
    ctx->buffer = ram_buffer;
    ctx->ram_size = ram_size;
    ctx->gain_factor = this->gain_factor;
    ctx->recorder_instance = this;

    // Launch Save Task (Lower Priority, Core 1)
    xTaskCreatePinnedToCore(save_task_wrapper, "audio_save", 4096, ctx, 1, NULL, 1);

    // CRITICAL: Resume Monitoring IMMEDIATELY
    // We do not wait for save to finish.
    recording_in_progress = false;
    should_resume_monitoring = true; 
  }

 private:
  void process_audio_chunk(char* raw_bytes, size_t len) {
      int32_t *samples = (int32_t *)raw_bytes;
      int num_samples = len / 4;
      if (num_samples == 0) return;

      double sum = 0;
      for (int i = 0; i < num_samples; i++) {
        float normalized = (float)samples[i] / 65536.0f; 
        sum += normalized * normalized;
      }
      float instant_rms = sqrt(sum / num_samples);
      this->current_rms = instant_rms;

      if (instant_rms > this->window_max_rms) this->window_max_rms = instant_rms;
      if (instant_rms < this->window_min_rms) this->window_min_rms = instant_rms;

      uint32_t now = esphome::millis();
      if (now - this->window_start_time > 500) {
          this->current_variance = this->window_max_rms - this->window_min_rms;
          this->window_min_rms = 100000.0f; this->window_max_rms = 0.0f;
          this->window_start_time = now;
      }
  }
};
}
