#include "encoder.hpp"

Encoder::Encoder(double wheel_radius, int ticks_per_revolution)
    : wheel_radius_(wheel_radius),
      ticks_per_revolution_(ticks_per_revolution),
      ticks_per_meter_(ticks_per_revolution / (2.0 * M_PI * wheel_radius)),
      offset_(0),
      encoder_(0),
      prev_encoder_(0),
      position_(0),
      prev_position_(0),
      multiplier_(0),
      initialized_(false),
      prev_position_initialized_(false) {}

void Encoder::update(int encoder) {
    if (!initialized_) {
        offset_ = encoder;
        prev_encoder_ = encoder;
        initialized_ = true;
    }

    encoder_ = encoder;

    if ((encoder_ < encoder_low_wrap_) && (prev_encoder_ > encoder_high_wrap_)) {
        multiplier_++;
    } else if ((encoder_ > encoder_high_wrap_) && (prev_encoder_ < encoder_low_wrap_)) {
        multiplier_--;
    }

    position_ = encoder_ + multiplier_ * encoder_range_ - offset_;
    prev_encoder_ = encoder_;
}

double Encoder::deltam() {
    if (!prev_position_initialized_) {
        prev_position_ = position_;
        prev_position_initialized_ = true;
        return 0.0;
    } else {
        double d = (prev_position_ - position_) / ticks_per_meter_;
        prev_position_ = position_;
        return d;
    }
}

