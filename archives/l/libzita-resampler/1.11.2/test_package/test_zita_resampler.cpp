#include <cstdlib>
#include <iostream>
#include <vector>

#include <zita-resampler/resampler.h>

int main() {
    Resampler resampler;
    if (resampler.setup(48000, 48000, 1, 16) != 0 || resampler.nchan() != 1) {
        return 1;
    }
    std::vector<float> input(128, 0.25f);
    std::vector<float> output(128, 0.0f);
    float *inputs[] = {input.data()};
    float *outputs[] = {output.data()};
    resampler.inp_list = inputs;
    resampler.out_list = outputs;
    resampler.inp_count = static_cast<unsigned int>(input.size());
    resampler.out_count = static_cast<unsigned int>(output.size());
    if (resampler.process() <= 0 || output[0] == 0.0f) {
        std::cerr << "resampler produced no output\n";
        return 1;
    }
    std::cout << "zita-resampler functional assertion passed\n";
    return 0;
}
