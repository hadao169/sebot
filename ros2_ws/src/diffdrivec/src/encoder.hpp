#ifndef ENCODER_HPP
#define ENCODER_HPP

#include <cmath>

class Encoder {
public:
    Encoder(double wheel_radius, int ticks_per_revolution);

    void update(int encoder);
    double deltam();

private:
    static constexpr int encoder_min_ = -32768;
    static constexpr int encoder_max_ = 32768;
    static constexpr int encoder_range_ = encoder_max_ - encoder_min_;
    static constexpr double encoder_low_wrap_ = ((encoder_max_ - encoder_min_) * 0.3) + encoder_min_;
    static constexpr double encoder_high_wrap_ = ((encoder_max_ - encoder_min_) * 0.7) + encoder_min_;

    double wheel_radius_;
    int ticks_per_revolution_;
    double ticks_per_meter_;

    int offset_;
    int encoder_;
    int prev_encoder_;
    double position_;
    double prev_position_;

    int multiplier_;
    bool initialized_ = false;
    bool prev_position_initialized_ = false;
};

#endif // ENCODER_HPP
