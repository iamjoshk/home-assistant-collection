import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

CONF_I2S_BCLK_PIN = "i2s_bclk_pin"
CONF_I2S_LRCLK_PIN = "i2s_lrclk_pin"
CONF_I2S_DIN_PIN = "i2s_din_pin"
CONF_GAIN = "gain"
CONF_DURATION = "duration"

DEPENDENCIES = ['esp32']

audio_recorder_ns = cg.esphome_ns.namespace('audio_recorder')
AudioRecorder = audio_recorder_ns.class_('AudioRecorder', cg.Component)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(AudioRecorder),
    cv.Required(CONF_I2S_BCLK_PIN): cv.int_,
    cv.Required(CONF_I2S_LRCLK_PIN): cv.int_,
    cv.Required(CONF_I2S_DIN_PIN): cv.int_,
    cv.Optional(CONF_GAIN, default=1): cv.int_range(min=1, max=100),
    cv.Optional(CONF_DURATION, default=10): cv.int_range(min=1, max=30), # Default 10s
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    
    cg.add(var.set_pins(
        config[CONF_I2S_BCLK_PIN],
        config[CONF_I2S_LRCLK_PIN],
        config[CONF_I2S_DIN_PIN]
    ))
    cg.add(var.set_gain(config[CONF_GAIN]))
    cg.add(var.set_duration(config[CONF_DURATION]))
